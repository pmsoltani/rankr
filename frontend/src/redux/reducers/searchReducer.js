import initialState from '../initialState'
import { r } from '../../routes'
import { apiClient } from '../../services'

export const SEARCH = '@@search/SEARCH'
export const SEARCH_SUCCESS = '@@search/SEARCH_SUCCESS'
export const SEARCH_FAILURE = '@@search/SEARCH_FAILURE'

export const CLEAR_CURRENT_SEARCH = '@@search/CLEAR_CURRENT_SEARCH'

export default function searchReducer (
  state = initialState.search,
  action = {}
) {
  switch (action.type) {
    case SEARCH:
      // Record the query this request is for, so out-of-order responses to
      // earlier queries can be discarded below.
      return { ...state, isLoading: true, latestQuery: action.meta?.q }
    case SEARCH_SUCCESS:
      // Ignore responses that don't match the most recent query (a slower
      // response to a shorter query must not clobber the current results).
      if (action.meta?.q !== state.latestQuery) return state
      return {
        ...state,
        isLoading: false,
        institutions: action.data.institutions,
        error: null
      }
    case SEARCH_FAILURE:
      if (action.meta?.q !== state.latestQuery) return state
      return {
        ...state,
        isLoading: false,
        error: action.error,
        institutions: []
      }
    case CLEAR_CURRENT_SEARCH:
      return { ...initialState.search }
    default:
      return state
  }
}

export const Actions = {}

Actions.search = args => {
  return apiClient({
    url: r.search.url,
    method: 'GET',
    types: {
      REQUEST: SEARCH,
      SUCCESS: SEARCH_SUCCESS,
      FAILURE: SEARCH_FAILURE
    },
    options: { data: {}, params: args },
    meta: { q: args.q }
  })
}

Actions.clearCurrentSearch = () => ({ type: CLEAR_CURRENT_SEARCH })
