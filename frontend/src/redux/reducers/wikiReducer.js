import initialState from '../initialState'
import { wikiApiClient } from '../../services'

export const GET_WIKI_PAGE = '@@wiki/GET_WIKI_PAGE'
export const GET_WIKI_PAGE_SUCCESS = '@@wiki/GET_WIKI_PAGE_SUCCESS'
export const GET_WIKI_PAGE_FAILURE = '@@wiki/GET_WIKI_PAGE_FAILURE'

export const SET_WIKI_PAGE = '@@wiki/SET_WIKI_PAGE'
export const CLEAR_CURRENT_WIKI_PAGE = '@@wiki/CLEAR_CURRENT_WIKI_PAGE'

export default function wikiReducer (state = initialState.wiki, action = {}) {
  switch (action.type) {
    case GET_WIKI_PAGE:
      return { ...state, isLoading: true }
    case GET_WIKI_PAGE_SUCCESS:
      return {
        ...state,
        isLoading: false,
        error: null,
        currentWikiPage: action.data
      }
    case GET_WIKI_PAGE_FAILURE:
      return { ...initialState.wiki, error: action.error }
    case CLEAR_CURRENT_WIKI_PAGE:
      return { ...initialState.wiki }
    default:
      return state
  }
}

export const Actions = {}

Actions.getWikiPage = args => {
  return wikiApiClient({
    url: args.url,
    types: {
      REQUEST: GET_WIKI_PAGE,
      SUCCESS: GET_WIKI_PAGE_SUCCESS,
      FAILURE: GET_WIKI_PAGE_FAILURE
    },
    options: { data: {}, params: args }
  })
}

Actions.clearCurrentWikiPage = () => ({ type: CLEAR_CURRENT_WIKI_PAGE })
