const initialState = {
  institutions: {
    isLoading: false,
    currentInstitutions: [],
    selectedInstitutions: [],
    error: null
  },
  rankings: {
    isLoading: false,
    currentRankings: { ranks: [], scores: [] },
    error: null
  },
  search: { isLoading: false, institutions: [], error: null },
  wiki: { isLoading: false, currentWikiPage: null, error: null }
}

export default initialState