import axios from 'axios'
import { formatURL } from '../utils'

const getClient = (contentType, token = null) => {
  const defaultOptions = {
    headers: {
      'Content-Type': contentType,
      Authorization: token ? `Bearer ${token}` : ''
    }
  }

  return {
    get: (url, data, options = {}) =>
      axios.get(url, { ...defaultOptions, ...options }),
    post: (url, data, options = {}) =>
      axios.post(url, data, { ...defaultOptions, ...options }),
    put: (url, data, options = {}) =>
      axios.put(url, data, { ...defaultOptions, ...options }),
    delete: (url, data, options = {}) =>
      axios.delete(url, { ...defaultOptions, ...options })
  }
}

/**
 *
 * @param {String} url: relative api endpoint url
 * @param {String} method: "GET", "POST", "PUT", "DELETE"
 * @param {Object} types: object with three keys representing the different action types: REQUEST, SUCCESS, FAILURE
 * @param {Object} options: object with potential data and query params
 * @param {Function} onSuccess: callback to run with the returned data, if any
 * @param {Function} onFailure: callback to run with the returned error, if any
 */
const apiClient = ({
  url,
  method,
  types: { REQUEST, SUCCESS, FAILURE },
  options: { contentType = 'application/json', data, params },
  onSuccess = res => ({
    type: res.type,
    success: true,
    status: res.status,
    data: res.data
  }),
  onFailure = res => ({
    type: res.type,
    success: false,
    status: res.status,
    error: res.error
  })
}) => {
  return async dispatch => {
    const token = window.localStorage.getItem('accessToken')
    const client = getClient(contentType, token)

    dispatch({ type: REQUEST })
    const urlPath = formatURL(url, params)

    try {
      const res = await client[method.toLowerCase()](urlPath, data)

      dispatch({ type: SUCCESS, data: res.data })

      return onSuccess({ type: SUCCESS, ...res })
    } catch (error) {
      console.log(error)
      dispatch({
        type: FAILURE,
        error: error?.response?.data ? error.response.data : error
      })

      return onFailure({
        type: FAILURE,
        status: error.status,
        error: error.response
      })
    }
  }
}

export default apiClient
