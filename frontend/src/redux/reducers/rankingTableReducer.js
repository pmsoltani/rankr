import initialState from '../initialState'
import { r } from '../../routes'
import { apiClient } from '../../services'

export const GET_RANKING_TABLE = '@@rankingTable/GET_RANKING_TABLE'
export const GET_RANKING_TABLE_SUCCESS =
  '@@rankingTable/GET_RANKING_TABLE_SUCCESS'
export const GET_RANKING_TABLE_FAILURE =
  '@@rankingTable/GET_RANKING_TABLE_FAILURE'

export const CLEAR_CURRENT_RANKING_TABLE =
  '@@rankingTable/CLEAR_CURRENT_RANKING_TABLE'

export default function rankingsReducer (
  state = initialState.rankingTable,
  action = {}
) {
  switch (action.type) {
    case GET_RANKING_TABLE:
      return { ...state, isLoading: true }
    case GET_RANKING_TABLE_SUCCESS:
      return {
        ...state,
        isLoading: false,
        error: null,
        currentRankingTable: action.data
      }
    case GET_RANKING_TABLE_FAILURE:
      return {
        ...state,
        isLoading: false,
        error: action.error,
        currentRankingTable: []
      }
    case CLEAR_CURRENT_RANKING_TABLE:
    default:
      return state
  }
}

export const Actions = {}

Actions.getRankingTable = args => {
  const { rankingSystem, year, ...rest } = args
  return apiClient({
    url: `${r.rankingTable.url}/${rankingSystem}/${year}`,
    method: 'GET',
    types: {
      REQUEST: GET_RANKING_TABLE,
      SUCCESS: GET_RANKING_TABLE_SUCCESS,
      FAILURE: GET_RANKING_TABLE_FAILURE
    },
    options: { data: {}, params: rest }
  })
}

Actions.clearCurrentRankingTable = () => ({
  type: CLEAR_CURRENT_RANKING_TABLE
})
