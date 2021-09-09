import React from 'react'
import { connect } from 'react-redux'
import { useNavigate } from 'react-router-dom'
import {
  EuiFieldText,
  EuiFormControlLayout,
  EuiIcon,
  EuiInputPopover,
  EuiPanel,
  EuiSelectable,
  EuiText
} from '@elastic/eui'

import '../../types'
import { institutionOutline } from '../../assets/images'
import { searchActions } from '../../redux/reducers'
import { r } from '../../routes'

const groupLabels = {
  institutions: { label: 'Institutions', isGroupLabel: true }
}

const SiteSearch = props => {
  /** @type Array.<Institution> */
  const institutions = props.institutions
  const { isLoading, search, error, clearCurrentSearch } = props
  const [popoverOpen, setPopoverOpen] = React.useState(false)
  const [searchValue, setSearchValue] = React.useState('')
  const [institutionResults, setInstitutionsResults] = React.useState([])
  const [searchResults, setSearchResults] = React.useState([])
  const inputRef = React.useRef(null)

  const navigate = useNavigate()
  const closePopover = () => setPopoverOpen(false)
  const resetSearch = () => {
    closePopover()
    setSearchValue('')
    clearCurrentSearch()
  }
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

  const emptyMessage = () => {
    let message = `Sorry! No results found for '${searchValue}'`
    if (!searchValue) message = 'Search for institutions'
    if (isLoading) message = ''
    return <EuiText size='xs'>{message}</EuiText>
  }

  const searchField = (
    <EuiPanel paddingSize='none' style={{ minWidth: 1000 }}>
      <EuiFormControlLayout
        id='site-search-field'
        fullWidth
        style={{ height: 88, minWidth: 1000 }}
      >
        <EuiFieldText
          aria-label='site-wide search field'
          fullWidth
          icon={() => <EuiIcon type='search' color='#a9a9a9' size='xl' />}
          inputRef={inputRef}
          isInvalid={error}
          isLoading={isLoading}
          onChange={onSearchChange}
          onFocus={() => {
            inputRef.current.scrollIntoView({ behavior: 'smooth' })
            setPopoverOpen(true)
          }}
          placeholder='Search for institutions'
          style={{
            fontSize: 30,
            height: 88,
            minWidth: 1000,
            paddingLeft: 60
          }}
          value={searchValue}
        />
      </EuiFormControlLayout>
    </EuiPanel>
  )

  return (
    <EuiInputPopover
      fullWidth
      closePopover={closePopover}
      input={searchField}
      isOpen={popoverOpen}
      panelPaddingSize='s'
    >
      <div style={{ height: 300 }}>
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
    </EuiInputPopover>
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
export default connect(mapStateToProps, mapDispatchToProps)(SiteSearch)
