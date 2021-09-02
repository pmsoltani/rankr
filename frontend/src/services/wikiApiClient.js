import wiki from 'wikipedia'

/**
 *
 * @param {String} url: wikipedia page url
 * @param {Object} types: object with three keys representing the different action types: REQUEST, SUCCESS, FAILURE
 * @param {Function} onSuccess: callback to run with the returned data, if any
 * @param {Function} onFailure: callback to run with the returned error, if any
 */
const wikiApiClient = ({
  url,
  types: { REQUEST, SUCCESS, FAILURE },
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
    dispatch({ type: REQUEST })

    try {
      const title = decodeURI(url.split('wiki/').pop())
      const res = await wiki.page(title, {}).then(page => page.summary())

      if (!res || !res.extract) throw new Error('Empty result')

      dispatch({ type: SUCCESS, data: res.extract })

      return onSuccess({ type: SUCCESS, ...res })
    } catch (error) {
      console.log(error)
      dispatch({
        type: FAILURE,
        error: error?.response?.data
          ? error.response.data
          : error?.message || String(error)
      })

      return onFailure({
        type: FAILURE,
        status: error.status,
        error: error.response
      })
    }
  }
}

export default wikiApiClient
