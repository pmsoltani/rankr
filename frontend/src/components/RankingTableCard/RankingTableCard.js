import React from 'react'
import { connect } from 'react-redux'
import { useNavigate } from 'react-router'
import {
  EuiFieldSearch,
  EuiFlexGroup,
  EuiFlexItem,
  EuiPanel
} from '@elastic/eui'

import { CountrySelect, RankingTable, SuperSelect } from '..'
import {
  rankingSystemsActions,
  rankingTableActions
} from '../../redux/reducers'
import { r } from '../../routes'

const RankingTableCard = props => {
  const { rankingSystem = '', year = '' } = props
  const { rankingSystems, rankingTable } = props.state
  const {
    getRankingSystems,
    clearCurrentRankingSystems,
    getRankingTable,
    clearCurrentRankingTable
  } = props
  const [systems, setSystems] = React.useState([])
  const [years, setYears] = React.useState([])
  const [selectedSystem, setSelectedSystem] = React.useState(rankingSystem)
  const [selectedYear, setSelectedYear] = React.useState(parseInt(year) || '')
  const [countries, setCountries] = React.useState([])
  const [selectedCountries, setSelectedCountries] = React.useState([])
  const [data, setData] = React.useState([])
  const [searchValue, setSearchValue] = React.useState('')

  const navigate = useNavigate()

  React.useEffect(() => {
    getRankingSystems()
    return () => clearCurrentRankingSystems()
  }, [clearCurrentRankingSystems, getRankingSystems])

  React.useEffect(() => {
    const systems = Object.keys(rankingSystems.currentRankingSystems)
    if (rankingSystems.currentRankingSystems && systems.length) {
      setSystems(systems)
      if (!selectedSystem) setSelectedSystem(systems[0])
    }
  }, [rankingSystems.currentRankingSystems, selectedSystem])

  React.useEffect(() => {
    if (systems.length && selectedSystem) {
      let years = rankingSystems.currentRankingSystems[selectedSystem]
      years = [...years].sort((a, b) => b - a)
      setYears(years)
      if (!selectedYear || !years.includes(selectedYear)) {
        setSelectedYear(years[0])
      }
    }
  }, [
    rankingSystems.currentRankingSystems,
    selectedSystem,
    selectedYear,
    systems
  ])

  React.useEffect(() => {
    if (selectedSystem && selectedYear) {
      navigate(`${r.rankingTable.url}/${selectedSystem}/${selectedYear}`)
      getRankingTable({
        rankingSystem: selectedSystem,
        year: selectedYear,
        limit: 0
      })
      setSearchValue('')
      setSelectedCountries([])
    }
    return () => clearCurrentRankingTable()
  }, [
    clearCurrentRankingTable,
    getRankingTable,
    navigate,
    selectedSystem,
    selectedYear
  ])

  React.useEffect(() => {
    if (
      rankingTable.currentRankingTable &&
      rankingTable.currentRankingTable.length
    ) {
      setData(rankingTable.currentRankingTable)
      const countriesArray = rankingTable.currentRankingTable.map(i => ({
        label: i.institution.country.country,
        value: { countryCode: i.institution.country.country_code }
      }))

      const uniqueCountires = Array.from(
        new Set(countriesArray.map(JSON.stringify))
      )
        .map(JSON.parse)
        .sort((a, b) => a.label.localeCompare(b.label))
      setCountries(uniqueCountires)
    }
  }, [rankingTable.currentRankingTable])

  React.useEffect(() => {
    if (selectedCountries.length) {
      const countries = selectedCountries.map(i => i.label)
      setData(
        rankingTable.currentRankingTable.filter(i =>
          countries.includes(i.institution.country.country)
        )
      )
    } else {
      setData(rankingTable.currentRankingTable)
    }
  }, [rankingTable.currentRankingTable, selectedCountries])

  const onSearchChange = React.useCallback(
    e => {
      setSearchValue(e.target.value)
      if (e.target.value) {
        setData(
          rankingTable.currentRankingTable.filter(i =>
            i.institution.soup
              .toLowerCase()
              .includes(e.target.value.toLowerCase())
          )
        )
      } else setData(rankingTable.currentRankingTable)
    },
    [rankingTable.currentRankingTable]
  )

  const onCountriesChange = selectedCountries => {
    setSelectedCountries(selectedCountries)
    setSearchValue('')
  }

  return (
    <EuiFlexGroup direction='rowReverse'>
      <EuiFlexItem grow={1}>
        <EuiFlexItem grow={false} style={{ marginBottom: '12px' }}>
          <SuperSelect
            key='ranking system select'
            isLoading={rankingSystems.isLoading}
            options={systems}
            onSelectChange={value => setSelectedSystem(value)}
            selectedValue={selectedSystem}
          />
        </EuiFlexItem>

        <EuiFlexItem grow={false} style={{ marginBottom: '12px' }}>
          <SuperSelect
            key='ranking year select'
            isLoading={rankingSystems.isLoading}
            options={years}
            onSelectChange={value => setSelectedYear(value)}
            selectedValue={selectedYear}
          />
        </EuiFlexItem>

        <EuiFlexItem grow={false} style={{ marginBottom: '12px' }}>
          <EuiFieldSearch
            fullWidth
            incremental
            value={searchValue}
            onChange={onSearchChange}
            placeholder='Institution filter'
            compressed
          />
        </EuiFlexItem>

        <EuiFlexItem grow={false}>
          <CountrySelect
            isLoading={rankingTable.isLoading}
            options={countries}
            onSelectChange={onCountriesChange}
            selectedValues={selectedCountries}
          />
        </EuiFlexItem>
      </EuiFlexItem>
      <EuiFlexItem grow={4}>
        <EuiPanel>
          <RankingTable isLoading={rankingTable.isLoading} data={data} />
        </EuiPanel>
      </EuiFlexItem>
    </EuiFlexGroup>
  )
}

const mapStateToProps = state => ({
  state: {
    rankingSystems: {
      isLoading: state.rankingSystems.isLoading,
      currentRankingSystems: state.rankingSystems.currentRankingSystems,
      error: state.rankingSystems.error
    },
    rankingTable: {
      isLoading: state.rankingTable.isLoading,
      currentRankingTable: state.rankingTable.currentRankingTable,
      error: state.rankingTable.error
    }
  }
})
const mapDispatchToProps = {
  getRankingSystems: rankingSystemsActions.getRankingSystems,
  clearCurrentRankingSystems: rankingSystemsActions.clearCurrentRankingSystems,
  getRankingTable: rankingTableActions.getRankingTable,
  clearCurrentRankingTable: rankingTableActions.clearCurrentRankingTable
}
export default connect(mapStateToProps, mapDispatchToProps)(RankingTableCard)
