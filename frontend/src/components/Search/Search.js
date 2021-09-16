import React from 'react'
import { connect } from 'react-redux'
import { useNavigate } from 'react-router-dom'
import {
  EuiButtonIcon,
  EuiFieldSearch,
  EuiIcon,
  EuiPopover,
  EuiPopoverTitle,
  EuiSelectable,
  EuiText
} from '@elastic/eui'

import '../../types'
import { institutionOutline } from '../../assets/images'
import { useWindowDimensions } from '../../hooks'
import { searchActions } from '../../redux/reducers'
import { r } from '../../routes'

const groupLabels = {
  institutions: { label: 'Institutions', isGroupLabel: true }
}

const Search = props => {
  /** @type Array.<Institution> */
  const institutions = props.institutions
  const { isLoading, search, error, clearCurrentSearch } = props
  const [popoverOpen, setPopoverOpen] = React.useState(false)
  const [searchValue, setSearchValue] = React.useState('')
  const [institutionResults, setInstitutionsResults] = React.useState([])
  const [searchResults, setSearchResults] = React.useState([])

  const navigate = useNavigate()
  const { width } = useWindowDimensions()

  const closePopover = () => setPopoverOpen(false)
  const resetSearch = () => {
    closePopover()
    setSearchValue('')
    clearCurrentSearch()
  }
  const onSearchButtonClick = () => setPopoverOpen(popoverOpen => !popoverOpen)
  const onSearchChange = React.useCallback(
    e => {
      setSearchValue(e.target.value)
      if (e.target.value) search({ q: e.target.value })
      else clearCurrentSearch()
    },
    [search, clearCurrentSearch]
  )
  const onSelectChange = changedSearchResults => {
    setSearchResults(changedSearchResults)
    const choice = changedSearchResults.filter(i => i.checked === 'on')[0]
    resetSearch()
    navigate(choice.url)
  }

  React.useEffect(() => {
    if (institutions.length) {
      setInstitutionsResults([
        groupLabels.institutions,
        ...institutions.map(i => ({
          key: i.id.toString(),
          label: i.name,
          searchableLabel: i.soup,
          prepend: <EuiIcon type={institutionOutline} />,
          url: `${r.institutions.url}/${i.grid_id}`
        }))
      ])
    }
    if (!institutions.length) setInstitutionsResults([])
  }, [institutions, setInstitutionsResults])

  React.useEffect(() => {
    return setSearchResults([...institutionResults])
  }, [institutionResults])

  const searchButton = (
    <EuiButtonIcon
      aria-label='Search button'
      color='text'
      display='empty'
      iconType='search'
      onClick={onSearchButtonClick}
      autoFocus={false}
    />
  )
  const emptyMessage = () => {
    let message = `Sorry! No results found for '${searchValue}'.`
    if (!searchValue) message = 'Search for institutions.'
    if (isLoading) message = ''
    return <EuiText size='xs'>{message}</EuiText>
  }

  return (
    <EuiPopover
      button={searchButton}
      isOpen={popoverOpen}
      closePopover={closePopover}
      panelPaddingSize='s'
    >
      <EuiPopoverTitle>
        <EuiFieldSearch
          placeholder='Search this'
          value={searchValue}
          onChange={onSearchChange}
          isClearable
          isInvalid={error}
          fullWidth
          isLoading={isLoading}
          aria-label='site-wide search field'
        />
      </EuiPopoverTitle>

      <div style={{ width: width > 500 ? 500 : '100%', height: 300 }}>
        <EuiSelectable
          aria-label='Search results'
          emptyMessage={emptyMessage()}
          height='full'
          listProps={{ showIcons: false }}
          onChange={onSelectChange}
          options={searchResults}
          singleSelection='always'
        >
          {list => list}
        </EuiSelectable>
      </div>
    </EuiPopover>
  )
}

const mapStateToProps = state => ({
  isLoading: state.search.isLoading,
  institutions: state.search.institutions,
  error: state.search.error
})
const mapDispatchToProps = {
  search: searchActions.search,
  clearCurrentSearch: searchActions.clearCurrentSearch
}
export default connect(mapStateToProps, mapDispatchToProps)(Search)
