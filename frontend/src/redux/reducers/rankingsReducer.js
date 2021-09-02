import initialState from '../initialState'
import { r } from '../../routes'
import { apiClient } from '../../services'

export const GET_RANKS_BY_INSTITUTION_ID =
  '@@rankings/GET_RANKS_BY_INSTITUTION_ID'
export const GET_RANKS_BY_INSTITUTION_ID_SUCCESS =
  '@@rankings/GET_RANKS_BY_INSTITUTION_ID_SUCCESS'
export const GET_RANKS_BY_INSTITUTION_ID_FAILURE =
  '@@rankings/GET_RANKS_BY_INSTITUTION_ID_FAILURE'

export const GET_SCORES_BY_INSTITUTION_ID =
  '@@rankings/GET_SCORES_BY_INSTITUTION_ID'
export const GET_SCORES_BY_INSTITUTION_ID_SUCCESS =
  '@@rankings/GET_SCORES_BY_INSTITUTION_ID_SUCCESS'
export const GET_SCORES_BY_INSTITUTION_ID_FAILURE =
  '@@rankings/GET_SCORES_BY_INSTITUTION_ID_FAILURE'

export const CLEAR_CURRENT_RANKINGS = '@@rankings/CLEAR_CURRENT_RANKINGS'

export default function rankingsReducer (
  state = initialState.rankings,
  action = {}
) {
  switch (action.type) {
    case GET_RANKS_BY_INSTITUTION_ID:
    case GET_SCORES_BY_INSTITUTION_ID:
      return { ...state, isLoading: true }
    case GET_RANKS_BY_INSTITUTION_ID_SUCCESS:
      return {
        ...state,
        isLoading: false,
        error: null,
        currentRankings: {
          ...state.currentRankings,
          ranks: Array.isArray(action.data) ? action.data : [action.data]
        }
      }
    case GET_SCORES_BY_INSTITUTION_ID_SUCCESS:
      return {
        ...state,
        isLoading: false,
        error: null,
        currentRankings: {
          ...state.currentRankings,
          scores: Array.isArray(action.data) ? action.data : [action.data]
        }
      }
    case GET_RANKS_BY_INSTITUTION_ID_FAILURE:
      return {
        ...state,
        isLoading: false,
        error: action.error,
        currentRankings: { ...state.currentRankings, ranks: [] }
      }
    case GET_SCORES_BY_INSTITUTION_ID_FAILURE:
      return {
        ...state,
        isLoading: false,
        error: action.error,
        currentRankings: { ...state.currentRankings, scores: [] }
      }
    case CLEAR_CURRENT_RANKINGS:
      return { ...initialState.rankings }
    default:
      return state
  }
}

export const Actions = {}

Actions.getRanksByInstitutionID = args => {
  return apiClient({
    url: `${r.rankings.url}/ranks`,
    method: 'GET',
    types: {
      REQUEST: GET_RANKS_BY_INSTITUTION_ID,
      SUCCESS: GET_RANKS_BY_INSTITUTION_ID_SUCCESS,
      FAILURE: GET_RANKS_BY_INSTITUTION_ID_FAILURE
    },
    options: { data: {}, params: args }
  })
}

Actions.getScoresByInstitutionID = args => {
  return apiClient({
    url: `${r.rankings.url}/scores`,
    method: 'GET',
    types: {
      REQUEST: GET_SCORES_BY_INSTITUTION_ID,
      SUCCESS: GET_SCORES_BY_INSTITUTION_ID_SUCCESS,
      FAILURE: GET_SCORES_BY_INSTITUTION_ID_FAILURE
    },
    options: { data: {}, params: args }
  })
}

Actions.clearCurrentRankings = () => ({ type: CLEAR_CURRENT_RANKINGS })
