import initialState from '../initialState'
import { r } from '../../routes'
import { apiClient } from '../../services'

export const GET_INSTITUTIONS = '@@institutions/GET_INSTITUTIONS'
export const GET_INSTITUTIONS_SUCCESS =
  '@@institutions/GET_INSTITUTIONS_SUCCESS'
export const GET_INSTITUTIONS_FAILURE =
  '@@institutions/GET_INSTITUTIONS_FAILURE'

export const GET_INSTITUTION_BY_ID = '@@institutions/GET_INSTITUTION_BY_ID'
export const GET_INSTITUTION_BY_ID_SUCCESS =
  '@@institutions/GET_INSTITUTION_BY_ID_SUCCESS'
export const GET_INSTITUTION_BY_ID_FAILURE =
  '@@institutions/GET_INSTITUTION_BY_ID_FAILURE'

export const SET_INSTITUTION = '@@institutions/SET_INSTITUTION'
export const CLEAR_CURRENT_INSTITUTIONS =
  '@@institutions/CLEAR_CURRENT_INSTITUTIONS'

export default function institutionsReducer (
  state = initialState.institutions,
  action = {}
) {
  switch (action.type) {
    case GET_INSTITUTIONS:
    case GET_INSTITUTION_BY_ID:
      return { ...state, isLoading: true }
    case GET_INSTITUTIONS_SUCCESS:
    case GET_INSTITUTION_BY_ID_SUCCESS:
      return {
        ...state,
        isLoading: false,
        error: null,
        currentInstitutions: Array.isArray(action.data)
          ? action.data
          : [action.data]
      }
    case GET_INSTITUTIONS_FAILURE:
    case GET_INSTITUTION_BY_ID_FAILURE:
      return {
        ...state,
        isLoading: false,
        error: action.error,
        currentInstitutions: []
      }
    case SET_INSTITUTION:
      return { ...state, selectedInstitutions: action.data }
    case CLEAR_CURRENT_INSTITUTIONS:
      return { ...initialState.institutions }
    default:
      return state
  }
}

export const Actions = {}

Actions.getInstitutions = args => {
  return apiClient({
    url: r.institutions.url,
    method: 'GET',
    types: {
      REQUEST: GET_INSTITUTIONS,
      SUCCESS: GET_INSTITUTIONS_SUCCESS,
      FAILURE: GET_INSTITUTIONS_FAILURE
    },
    options: { data: {}, params: args }
  })
}

Actions.getInstitutionByID = ({ institutionID }) => {
  return apiClient({
    url: `${r.institutions.url}/${institutionID}/`,
    method: 'GET',
    types: {
      REQUEST: GET_INSTITUTION_BY_ID,
      SUCCESS: GET_INSTITUTION_BY_ID_SUCCESS,
      FAILURE: GET_INSTITUTION_BY_ID_FAILURE
    },
    options: { data: {}, params: {} }
  })
}

Actions.setInstitution = institution => ({
  type: SET_INSTITUTION,
  data: institution
})

Actions.clearCurrentInstitutions = () => ({ type: CLEAR_CURRENT_INSTITUTIONS })
