import * as c from '../config'

/**
 * Constructs API request URLs
 *
 * @param {string} url: url string representing relative path to api endpoint
 * @param {Object.<string, any>} params: query params to format at end of url
 */
export const formatURL = (endpoint, params = [], serverSide = true) => {
  const defaultBaseURL = new URL(`http://${c.SERVER_HOST}:${c.SERVER_PORT}`)
  const fullURL =
    c.APP_ENV === 'prod' ? new URL(c.REMOTE_SERVER_URL) : defaultBaseURL

  const endpointPath = [
    ...(serverSide ? c.SERVER_API_V1_STR.split('/') : []),
    ...endpoint.split('/')
  ]
    .filter(i => i)
    .join('/')
  fullURL.pathname = endpointPath

  const searchParams = new URLSearchParams()
  Object.entries(params).forEach(([key, value]) => {
    Array.isArray(value)
      ? value.forEach(v => searchParams.append(key, v))
      : searchParams.append(key, value)
  })
  fullURL.search = searchParams

  return fullURL
}

/**
 * Creates the OpenStreetMap URL for the specified lat & lng
 *
 * @param {string} lat: position's latitude
 * @param {string} lng: position's longitude
 * @returns {string}
 */
export const openStreetMapURL = (lat, lng) => {
  if (lat && lng) {
    const fullURL = new URL(c.openStreetMapBase)
    const searchParams = new URLSearchParams({ mlat: lat, mlon: lng, zoom: 18 })
    fullURL.search = searchParams
    return fullURL.href
  }
}

/**
 * Creates the GRID URL for the specified gridID
 *
 * @param {string} gridID: institution's GRID ID
 * @returns {string}
 */
export const gridURL = gridID => {
  if (gridID) {
    const fullURL = new URL(c.gridBase)
    fullURL.pathname = ['institutes', gridID].join('/')
    return fullURL.href
  }
}
