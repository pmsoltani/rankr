import { combineReducers } from 'redux'

import {
  compareReducer,
  institutionsReducer,
  rankingsReducer,
  rankingSystemsReducer,
  rankingTableReducer,
  searchReducer,
  wikiReducer
} from '.'

const rootReducer = combineReducers({
  compare: compareReducer,
  institutions: institutionsReducer,
  rankings: rankingsReducer,
  rankingSystems: rankingSystemsReducer,
  rankingTable: rankingTableReducer,
  search: searchReducer,
  wiki: wikiReducer
})

export default rootReducer
