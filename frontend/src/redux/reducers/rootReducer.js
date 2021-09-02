import { combineReducers } from 'redux'

import {
  institutionsReducer,
  rankingsReducer,
  searchReducer,
  wikiReducer
} from '.'

const rootReducer = combineReducers({
  institutions: institutionsReducer,
  rankings: rankingsReducer,
  search: searchReducer,
  wiki: wikiReducer
})

export default rootReducer
