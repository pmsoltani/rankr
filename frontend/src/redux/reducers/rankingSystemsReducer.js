import initialState from '../initialState'
import { r } from '../../routes'
import { apiClient } from '../../services'

export const GET_RANKING_SYSTEMS = '@@rankingSystems/GET_RANKING_SYSTEMS'
export const GET_RANKING_SYSTEMS_SUCCESS =
  '@@rankingSystems/GET_RANKING_SYSTEMS_SUCCESS'
export const GET_RANKING_SYSTEMS_FAILURE =
  '@@rankingSystems/GET_RANKING_SYSTEMS_FAILURE'

export const CLEAR_CURRENT_RANKING_SYSTEMS =
  '@@rankingSystems/CLEAR_CURRENT_RANKING_SYSTEMS'

export default function rankingsReducer (
  state = initialState.rankingSystems,
  action = {}
) {
  switch (action.type) {
    case GET_RANKING_SYSTEMS:
      return { ...state, isLoading: true }
    case GET_RANKING_SYSTEMS_SUCCESS:
      return {
        ...state,
        isLoading: false,
        error: null,
        currentRankingSystems: action.data
      }
    case GET_RANKING_SYSTEMS_FAILURE:
      return {
        ...state,
        isLoading: false,
        error: action.error,
        currentRankingSystems: {}
      }
    case CLEAR_CURRENT_RANKING_SYSTEMS:
    default:
      return state
  }
}

export const Actions = {}

Actions.getRankingSystems = () => {
  return apiClient({
    url: `${r.rankingSystems.url}`,
    method: 'GET',
    types: {
      REQUEST: GET_RANKING_SYSTEMS,
      SUCCESS: GET_RANKING_SYSTEMS_SUCCESS,
      FAILURE: GET_RANKING_SYSTEMS_FAILURE
    },
    options: { data: {}, params: {} }
  })
}

Actions.clearCurrentRankingSystems = () => ({
  type: CLEAR_CURRENT_RANKING_SYSTEMS
})
