import api from './api'

const storage = new Map()
const pending = new Map()

const REFRESH_RATE = 1000

const store = {

  schemas: {},

  /**
   * Find a resource in the store associated with the given id.
   * Returns a Promise resolving to the proxied queried resource.
   * It rejects to the server response, giving access to status codes.
   *
   * @param {string} id - The id of the queried resource.
   * @param {boolean} handle - Whether the id given is actually a handle.
   */
  get(id) {
    if (storage.has(id)) {
      return Promise.resolve(storage.get(id))
    }
    else {
      let url

      url = api.resourceURL(id)

      if (pending.has(url))
        return pending.get(url)
      else
        return store.fetchResource(url)
    }
  },


  /**
   * Delete a resource associated with the given id.
   * Returns a Promise resolving to an empty object.
   * It rejects to the server response, giving access to status codes.
   *
   * @param {string} id - The uuid of the queried resource.
   */
  delete(id) {
    return api
      .delete(tozti.api.resourceURL(id))
      .then(() => {
        if (storage.has(id)) {
          storage.delete(id)
        }
        return {}
      })
  },


  /**
   * Update a resource in the server store.
   * Returns a Promise resolving to the new resource.
   * It rejects to the server response, giving access to status codes.
   *
   * The update is a patch, meaning there is no need to define every
   * resource attribute and relationship.
   * The only required field is the id.
   *
   * @param {Object} resource - The resource to be updated.
   */
  update(resource) {
    return api
      .patch(tozti.api.resourceURL(resource.id), { data: resource })
      .then(({ data }) => {
        return store.save(data)
      })
  },


  /**
   * Create a new resource in the server store.
   * Returns a Promise resolving to the new resource.
   * It rejects to the server response, giving access to status codes.
   *
   * If the `save` argument is set to `false`, the resource will not be saved
   * in the local store.
   *
   * @param {Object} resource - The resource to be updated.
   * @param {boolean} save - Whether we want to save the resource in the local store.
   */
  create(resource, save = true) {
    return api
      .post(api.endpoints.resources, { data: resource })
      .then(({ data }) => save ? store.save(data) : data)
  },


  // TODO(flupe): choose a more explicit name?
  //              right now we might think it saves a resource on the server.

  /**
   * Stores a resource in the local cache.
   * This should only be used with resources coming from the server.
   *
   * @param {Object} resource - The resource to be added in the store.
   */
  save(resource) {
    if (storage.has(resource.id)) {
      return updateProxy(storage.get(resource.id), resource)
    }
    else {
      let proxy = createProxy(resource)
      storage.set(resource.id, proxy)
      return proxy
    }
  },


  /**
   * Fetch a resource from the server associated with the given id.
   * Returns a Promise resolving to the proxied queried resource.
   *
   * @param {string} id - The uuid of the queried resource.
   */
  fetchResource(url) {
    const promise = api
      .get(url)
      .then(({ data }) => {
        return store.save(data)
      })

    pending.set(url, promise)

    // maybe move this inside the promise definition.
    // note that this is not very robust to other type of queries.
    promise.finally(_ => {
      pending.delete(url)
    })

    return promise
  },


  /**
   * Fetch the linkage of every resource of a given type.
   * Returns a Promise resolving to an array of linkages.
   *
   * @param {string} type - The queried type.
   */
  ofType(type) {
    return api
      .get(api.typeURL(type))
      .then(({ data }) => data)
  },


  /**
   * Fetch every resource of a given type.
   * Returns a Promise resolving to an array of resources.
   *
   * It is often preferable to use ofType(), as the promise 
   * returned by fetchOfType() only resolves once every resource
   * has been fetched.
   *
   * @param {string} type - The queried type.
   */
  fetchOfType(type) {
    return store.ofType(type)
      .then(resources => Promise.all(resources.map(res => store.get(res.id))))
  },


  handle: {
    get(handle) {
      return api
        .get(api.handleURL(handle))
        .then(({ data }) => tozti.store.get(data.id))
    }
  },


  rels: {
    // until we figure out how to cleanly merge two objects,
    // we do not care about the server response and apply changes locally.

    /** 
     * Fetch the resources of a relationship.
     * Returns a Promise.
     * For a to-one relationship, resolves to the resource if it exists.
     * For a to-many relationship, resolves to an array of resources.
     *
     * @param {Object} relationship - The relationship.
     */
    fetch({ data }) {
      if (Array.isArray(data)) {
        return Promise.all(data.map(({ id }) => store.get(id)))
      }
      else return store.get(data.id)
    },


    /** 
     * Add linkages to to-many and keyed relationships.
     * Returns a Promise resolving to the relationship itself.
     *
     *  A linkage is simply an object with an id.
     *
     * @param {Object} relationship - The relationship.
     * @param {...Object} linkages - The linkages to be added.
     */
    add(rel, ...linkages) {
      // to-many relationship
      if (Array.isArray(rel.data)) {
        return api
          .post( rel.self, { data: linkages })
          .then(() => {
            rel.data.push(...linkages)
            return rel
          })
      }
      else {
        linkages = linkages[0] 
        return api
          .post( rel.self, { data: linkages})
          .then(() => {
            for (let k in linkages) {
              Vue.set(rel.data, k, linkages[k])
            }
            return rel
          })
      }
    },


    update(rel, data) {
      // TODO(flupe)
    },


    /** 
     * Deletes linkages of a to-many relationship.
     * Returns a Promise resolving to the relationship itself.
     *
     *  A linkage is simply an object with an id.
     *
     * @param {Object} relationship - The relationship.
     * @param {...Object} linkages - The linkages to be removed.
     */
    delete(rel, ...linkages) {
      return api
        .delete(api.origin + rel.self, { data: linkages })
        .then(() => {

          // deletion in n^2 because why do better?
          linkages.forEach(({ id }) => {
            let index = rel.data.findIndex(link => link.id == id)
            if (index > -1) {
              rel.data.splice(index, 1)
            }
          })

          return rel
        })
    }
  }

}

// TODO(flupe):
//  look at how reactivity really works in Vue.
//  for now, we will simply store the plain data
//  the motivation for proxying resource is that we can enforce immutability.
function createProxy(data) {
  return data
}


// TODO(flupe):
//  for now we recursively walk on the old resource, and update the fields.
//  this works fine with vue watchers, but is not very pretty.
function updateProxy(old, update) {
  Object.assign(old, update)
}


// TODO(liautaud):
//  Remove this, because it is the worst possible implementation of real-time
//  updates. However, we need something like this until we get have a proper
//  message queue system -- which we won't have in time for the demo.
let refreshInterval = setInterval(() => {
  for (let id of storage.keys()) {
    let url = api.resourceURL(id)
    store.fetchResource(url)
  }
}, REFRESH_RATE)


export default store

