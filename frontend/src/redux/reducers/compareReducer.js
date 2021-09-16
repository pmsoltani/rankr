import initialState from '../initialState'
import { r } from '../../routes'
import { apiClient } from '../../services'

export const SEARCH_FOR_COMPARE = '@@compare/SEARCH_FOR_COMPARE'
export const SEARCH_FOR_COMPARE_SUCCESS = '@@compare/SEARCH_FOR_COMPARE_SUCCESS'
export const SEARCH_FOR_COMPARE_FAILURE = '@@compare/SEARCH_FOR_COMPARE_FAILURE'
export const CLEAR_SEARCH_FOR_COMPARE = '@@compare/CLEAR_SEARCH_FOR_COMPARE'

export const SET_INSTITUTIONS_FOR_COMPARE =
  '@@compare/SET_INSTITUTIONS_FOR_COMPARE'
export const SET_RANKING_SYSTEM_FOR_COMPARE =
  '@@compare/SET_RANKING_SYSTEM_FOR_COMPARE'
export const SET_RANKING_YEAR_FOR_COMPARE =
  '@@compare/SET_RANKING_YEAR_FOR_COMPARE'

export const GET_RANKS_BY_INSTITUTION_IDS_FOR_COMPARE =
  '@@compare/GET_RANKS_BY_INSTITUTION_IDS_FOR_COMPARE'
export const GET_RANKS_BY_INSTITUTION_IDS_FOR_COMPARE_SUCCESS =
  '@@compare/GET_RANKS_BY_INSTITUTION_IDS_FOR_COMPARE_SUCCESS'
export const GET_RANKS_BY_INSTITUTION_IDS_FOR_COMPARE_FAILURE =
  '@@compare/GET_RANKS_BY_INSTITUTION_IDS_FOR_COMPARE_FAILURE'

export const GET_SCORES_BY_INSTITUTION_IDS_FOR_COMPARE =
  '@@compare/GET_SCORES_BY_INSTITUTION_IDS_FOR_COMPARE'
export const GET_SCORES_BY_INSTITUTION_IDS_FOR_COMPARE_SUCCESS =
  '@@compare/GET_SCORES_BY_INSTITUTION_IDS_FOR_COMPARE_SUCCESS'
export const GET_SCORES_BY_INSTITUTION_IDS_FOR_COMPARE_FAILURE =
  '@@compare/GET_SCORES_BY_INSTITUTION_IDS_FOR_COMPARE_FAILURE'

export const CLEAR_RANKS_FOR_COMPARE = '@@compare/CLEAR_RANKS_FOR_COMPARE'
export const CLEAR_SCORES_FOR_COMPARE = '@@compare/CLEAR_SCORES_FOR_COMPARE'

export default function compareReducer (
  state = initialState.compare,
  action = {}
) {
  switch (action.type) {
    case SEARCH_FOR_COMPARE:
      return { ...state, isLoadingSearch: true }
    case SEARCH_FOR_COMPARE_SUCCESS:
      return {
        ...state,
        isLoadingSearch: false,
        institutions: action.data.institutions,
        errorSearch: null
      }
    case SEARCH_FOR_COMPARE_FAILURE:
      return {
        ...state,
        isLoadingSearch: false,
        errorSearch: action.error,
        institutions: []
      }
    case CLEAR_SEARCH_FOR_COMPARE:
      return {
        ...state,
        isLoadingSearch: false,
        institutions: [],
        errorSearch: null
      }
    case SET_INSTITUTIONS_FOR_COMPARE:
      return { ...state, selectedInstitutions: action.data }
    case SET_RANKING_SYSTEM_FOR_COMPARE:
      return { ...state, selectedRankingSystem: action.data }
    case SET_RANKING_YEAR_FOR_COMPARE:
      return { ...state, selectedRankingYear: action.data }
    case GET_RANKS_BY_INSTITUTION_IDS_FOR_COMPARE:
      return { ...state, isLoadingRanks: true }
    case GET_SCORES_BY_INSTITUTION_IDS_FOR_COMPARE:
      return { ...state, isLoadingScores: true }
    case GET_RANKS_BY_INSTITUTION_IDS_FOR_COMPARE_SUCCESS:
      return {
        ...state,
        isLoadingRanks: false,
        currentRankings: {
          ...state.currentRankings,
          ranks: Array.isArray(action.data) ? action.data : [action.data]
        },
        errorRankings: null
      }
    case GET_SCORES_BY_INSTITUTION_IDS_FOR_COMPARE_SUCCESS:
      return {
        ...state,
        isLoadingScores: false,
        currentRankings: {
          ...state.currentRankings,
          scores: Array.isArray(action.data) ? action.data : [action.data]
        },
        errorRankings: null
      }
    case GET_RANKS_BY_INSTITUTION_IDS_FOR_COMPARE_FAILURE:
      return {
        ...state,
        isLoadingRanks: false,
        errorRankings: action.error,
        currentRankings: { ...state.currentRankings, ranks: [] }
      }
    case GET_SCORES_BY_INSTITUTION_IDS_FOR_COMPARE_FAILURE:
      return {
        ...state,
        isLoadingScores: false,
        errorRankings: action.error,
        currentRankings: { ...state.currentRankings, scores: [] }
      }
    case CLEAR_RANKS_FOR_COMPARE:
      return {
        ...state,
        isLoadingRanks: false,
        currentRankings: { ...state.currentRankings, ranks: [] },
        errorRankings: null
      }
    case CLEAR_SCORES_FOR_COMPARE:
      return {
        ...state,
        isLoadingScores: false,
        currentRankings: { ...state.currentRankings, scores: [] },
        errorRankings: null
      }
    default:
      return state
  }
}

export const Actions = {}

Actions.searchForCompare = args => {
  return apiClient({
    url: r.search.url,
    method: 'GET',
    types: {
      REQUEST: SEARCH_FOR_COMPARE,
      SUCCESS: SEARCH_FOR_COMPARE_SUCCESS,
      FAILURE: SEARCH_FOR_COMPARE_FAILURE
    },
    options: { data: {}, params: args }
  })
}

Actions.clearSearchForCompare = () => ({ type: CLEAR_SEARCH_FOR_COMPARE })

Actions.setInstitutionsForCompare = institutions => ({
  type: SET_INSTITUTIONS_FOR_COMPARE,
  data: institutions
})

Actions.setRankingSystemForCompare = rankingSystem => ({
  type: SET_RANKING_SYSTEM_FOR_COMPARE,
  data: rankingSystem
})

Actions.setRankingYearForCompare = rankingYear => ({
  type: SET_RANKING_YEAR_FOR_COMPARE,
  data: rankingYear
})

Actions.getRanksByInstitutionIDsForCompare = args => {
  return apiClient({
    url: `${r.rankings.url}/i/metric`,
    method: 'GET',
    types: {
      REQUEST: GET_RANKS_BY_INSTITUTION_IDS_FOR_COMPARE,
      SUCCESS: GET_RANKS_BY_INSTITUTION_IDS_FOR_COMPARE_SUCCESS,
      FAILURE: GET_RANKS_BY_INSTITUTION_IDS_FOR_COMPARE_FAILURE
    },
    options: { data: {}, params: { ...args, metrics: ['Rank'], limit: 0 } }
  })
}

Actions.getScoresByInstitutionIDsForCompare = args => {
  return apiClient({
    url: `${r.rankings.url}/i/metric`,
    method: 'GET',
    types: {
      REQUEST: GET_SCORES_BY_INSTITUTION_IDS_FOR_COMPARE,
      SUCCESS: GET_SCORES_BY_INSTITUTION_IDS_FOR_COMPARE_SUCCESS,
      FAILURE: GET_SCORES_BY_INSTITUTION_IDS_FOR_COMPARE_FAILURE
    },
    options: { data: {}, params: { ...args, limit: 0 } }
  })
}

Actions.clearRanksForCompare = () => ({ type: CLEAR_RANKS_FOR_COMPARE })
Actions.clearScoresForCompare = () => ({ type: CLEAR_SCORES_FOR_COMPARE })
