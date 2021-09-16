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
  const onChange = selectedOptions => setInstitutionsForCompare(selectedOptions)

  React.useEffect(() => {
    institutions.length
      ? setOptions(
          institutions.map(i => ({ key: i.id.toString(), label: i.name }))
        )
      : setOptions([])
  }, [institutions])

  const onSearchChange = React.useCallback(
    value => {
      if (value && selectedInstitutions.length < 3) {
        searchForCompare({ q: value })
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
