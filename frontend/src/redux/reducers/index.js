export {
  default as institutionsReducer,
  Actions as institutionActions,
  GET_INSTITUTIONS,
  GET_INSTITUTIONS_SUCCESS,
  GET_INSTITUTIONS_FAILURE,
  GET_INSTITUTION_BY_ID,
  GET_INSTITUTION_BY_ID_SUCCESS,
  GET_INSTITUTION_BY_ID_FAILURE,
  SET_INSTITUTION,
  CLEAR_CURRENT_INSTITUTIONS
} from './institutionsReducer'

export {
  default as rankingsReducer,
  Actions as rankingActions,
  GET_RANKS_BY_INSTITUTION_ID,
  GET_RANKS_BY_INSTITUTION_ID_SUCCESS,
  GET_RANKS_BY_INSTITUTION_ID_FAILURE,
  GET_SCORES_BY_INSTITUTION_ID,
  GET_SCORES_BY_INSTITUTION_ID_SUCCESS,
  GET_SCORES_BY_INSTITUTION_ID_FAILURE,
  CLEAR_CURRENT_RANKINGS
} from './rankingsReducer'

export {
  default as searchReducer,
  Actions as searchActions,
  SEARCH,
  SEARCH_SUCCESS,
  SEARCH_FAILURE,
  CLEAR_CURRENT_SEARCH
} from './searchReducer'

export {
  default as wikiReducer,
  Actions as wikiActions,
  GET_WIKI_PAGE,
  GET_WIKI_PAGE_SUCCESS,
  GET_WIKI_PAGE_FAILURE,
  CLEAR_CURRENT_WIKI_PAGE
} from './wikiReducer'
