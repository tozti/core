/**
 * A very generic API to communicate with the tozti backend
 */

const API = {}

API.origin = window.location.origin
API.prefix = `${API.origin}/api`

API.endpoints = {
  resources: `${API.prefix}/store/resources`,
  types: `${API.prefix}/store/by-type`,
  me: `${API.prefix}/auth/me`,
  login: `${API.prefix}/auth/login`,
  signup: `${API.prefix}/auth/signup`,
}

API.resourceURL = id => `${API.endpoints.resources}/${id}`
API.typeURL = type => `${API.endpoints.types}/${type}`

const config = {
  mode: 'same-origin',

  // allow the request to send & receive cookies
  credentials: 'same-origin',

  // conforming to JSON API
  headers: new Headers({
    'Content-type': 'application/vnd.api+json',
    'Accept': 'application/vnd.api+json'
  })
}

function request(url, config) {
  // the fetch() Promise always resolves to the response,
  // whether it was successful or not
  return fetch(url, config)
    .then(res => res.ok ? res.json() : Promise.reject(res))
    .catch(err => console.log(err))
}

// TODO(flupe): factor this out?

API.post = (url, data = {}) => {
  const conf = Object.assign({
    method: 'POST',
    body: JSON.stringify(data),
  }, config)
  return request(url, conf)
}

API.patch = (url, data = {}) => {
  const conf = Object.assign({
    method: 'PATCH',
    body: JSON.stringify(data),
  }, config)
  return request(url, conf)
}

API.delete = (url, data = {}) => {
  const conf = Object.assign({
    method: 'DELETE',
    body: JSON.stringify(data),
  }, config)
  return request(url, conf)
}

API.get = url => {
  const conf = Object.assign({}, config, { method: 'GET' })
  return request(url, conf)
}

export default API
