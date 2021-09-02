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
      return { ...state, isLoading: true }
    case SEARCH_SUCCESS:
      return {
        ...state,
        isLoading: false,
        institutions: action.data.institutions,
        error: null
      }
    case SEARCH_FAILURE:
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
    options: { data: {}, params: args }
  })
}

Actions.clearCurrentSearch = () => ({ type: CLEAR_CURRENT_SEARCH })
