import React from 'react'
import { connect } from 'react-redux'
import { EuiComboBox, EuiFormRow } from '@elastic/eui'

import { compareActions } from '../../redux/reducers'
import '../../types'

const CompareSearch = props => {
  /** @type Array.<Institution> */
  const institutions = props.institutions
  const {
    isLoadingSearch,
    selectedInstitutions,
    searchForCompare,
    clearSearchForCompare,
    setInstitutionsForCompare
  } = props

  const [options, setOptions] = React.useState([])
  const debounceRef = React.useRef(null)
  const onChange = selectedOptions => setInstitutionsForCompare(selectedOptions)

  React.useEffect(() => {
    institutions.length
      ? setOptions(
          institutions.map(i => ({ key: i.id.toString(), label: i.name }))
        )
      : setOptions([])
  }, [institutions])

  // Debounce the lookup so a request fires only once typing settles (~300ms);
  // the reducer additionally drops any out-of-order response to a stale query.
  const onSearchChange = React.useCallback(
    value => {
      clearTimeout(debounceRef.current)
      if (value && selectedInstitutions.length < 3) {
        debounceRef.current = setTimeout(() => searchForCompare({ q: value }),300)
      } else clearSearchForCompare()
    },
    [searchForCompare, clearSearchForCompare, selectedInstitutions]
  )

  return (
    <EuiFormRow
      label={selectedInstitutions.length >= 3 && 'Select up to 3 institutions'}
      isInvalid={selectedInstitutions.length > 3}
    >
      <EuiComboBox
        async
        isLoading={isLoadingSearch}
        isInvalid={selectedInstitutions.length > 3}
        onChange={onChange}
        onSearchChange={onSearchChange}
        options={options}
        placeholder='Select institutions to compare'
        selectedOptions={selectedInstitutions}
      />
    </EuiFormRow>
  )
}

const mapStateToProps = state => ({
  isLoadingSearch: state.compare.isLoadingSearch,
  institutions: state.compare.institutions,
  errorSearch: state.compare.errorSearch,
  selectedInstitutions: state.compare.selectedInstitutions
})
const mapDispatchToProps = {
  searchForCompare: compareActions.searchForCompare,
  clearSearchForCompare: compareActions.clearSearchForCompare,
  setInstitutionsForCompare: compareActions.setInstitutionsForCompare
}
export default connect(mapStateToProps, mapDispatchToProps)(CompareSearch)
