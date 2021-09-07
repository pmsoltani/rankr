import { combineReducers } from 'redux'

import {
  institutionsReducer,
  rankingsReducer,
  rankingSystemsReducer,
  rankingTableReducer,
  searchReducer,
  wikiReducer
} from '.'

const rootReducer = combineReducers({
  institutions: institutionsReducer,
  rankings: rankingsReducer,
  rankingSystems: rankingSystemsReducer,
  rankingTable: rankingTableReducer,
  search: searchReducer,
  wiki: wikiReducer
})

export default rootReducer
