import React from 'react'
import { connect } from 'react-redux'
import {
  EuiEmptyPrompt,
  EuiFlexGroup,
  EuiFlexItem,
  EuiSpacer
} from '@elastic/eui'

import { CompareSearch, LineChart, RadarChart, SuperSelect } from '..'
import * as c from '../../config'
import { compareActions, rankingSystemsActions } from '../../redux/reducers'
import '../../types'
import { compareRankChartProps, compareScoreChartProps } from '../../utils'

const ComparePage = props => {
  /** @type {{
    selectedInstitutions: Array.<{ key: string, label: string }>,
    selectedRankingSystem: string,
    selectedRankingYear: number,
    isLoadingRanks: boolean,
    isLoadingScores: boolean,
    currentRankings: { ranks: Array.<Ranking>, scores: Array.<Ranking> },
    errorRankings: any
  }} */
  const compare = props.state.compare
  /** @type {Institution} */
  const inst = props.inst
  /** @type {{
    isLoading: boolean,
    currentRankingSystems: Object.<string, Array.<number>>,
    error: any
  }} */
  const rankingSystems = props.state.rankingSystems
  const {
    getRankingSystems,
    clearCurrentRankingSystems,

    setInstitutionsForCompare,
    setRankingSystemForCompare,
    setRankingYearForCompare,

    getRanksByInstitutionIDsForCompare,
    getScoresByInstitutionIDsForCompare,
    clearRanksForCompare,
    clearScoresForCompare
  } = props

  const [systems, setSystems] = React.useState([])
  const [years, setYears] = React.useState([])
  const [compareRankChart, setCompareRankChart] = React.useState(null)
  const [compareScoreChart, setCompareScoreChart] = React.useState(null)
  const noChartMessage = (
    <EuiEmptyPrompt
      iconType='glasses'
      style={{ height: '400px' }}
      body={<p>Select an institution to compare.</p>}
    />
  )

  React.useEffect(() => {
    if (inst.id) {
      getRankingSystems()
      setInstitutionsForCompare([{ key: inst.id.toString(), label: inst.name }])
    }
    return () => clearCurrentRankingSystems()
  }, [
    clearCurrentRankingSystems,
    getRankingSystems,
    inst,
    setInstitutionsForCompare
  ])

  React.useEffect(() => {
    const systems = Object.keys(rankingSystems.currentRankingSystems)
    if (rankingSystems.currentRankingSystems && systems.length) {
      setSystems(systems)
      if (!compare.selectedRankingSystem) setRankingSystemForCompare(systems[0])
    }
  }, [
    compare.selectedRankingSystem,
    rankingSystems.currentRankingSystems,
    setRankingSystemForCompare
  ])

  React.useEffect(() => {
    if (systems.length && compare.selectedRankingSystem) {
      const selectedSystem = compare.selectedRankingSystem
      let years = rankingSystems.currentRankingSystems[selectedSystem]
      years = [...years].sort((a, b) => b - a)
      setYears(years)
      if (
        !compare.selectedRankingYear ||
        !years.includes(compare.selectedRankingYear)
      ) {
        setRankingYearForCompare(years[0])
      }
    }
  }, [
    rankingSystems.currentRankingSystems,
    compare.selectedRankingSystem,
    compare.selectedRankingYear,
    setRankingYearForCompare,
    systems
  ])

  React.useEffect(() => {
    if (inst.id && !compare.selectedInstitutions.length) {
      setInstitutionsForCompare([{ key: inst.id.toString(), label: inst.name }])
    }
  }, [compare.selectedInstitutions, inst, setInstitutionsForCompare])

  React.useEffect(() => {
    if (
      compare.selectedInstitutions.length > 1 &&
      compare.selectedRankingSystem
    ) {
      getRanksByInstitutionIDsForCompare({
        institution_ids: compare.selectedInstitutions.map(i => i.key),
        ranking_system: compare.selectedRankingSystem
      })
    }
    return () => clearRanksForCompare()
  }, [
    clearRanksForCompare,
    compare.selectedInstitutions,
    compare.selectedRankingSystem,
    getRanksByInstitutionIDsForCompare
  ])

  React.useEffect(() => {
    if (
      compare.selectedInstitutions.length > 1 &&
      compare.selectedRankingSystem &&
      compare.selectedRankingYear
    ) {
      getScoresByInstitutionIDsForCompare({
        institution_ids: compare.selectedInstitutions.map(i => i.key),
        ranking_system: compare.selectedRankingSystem,
        year: compare.selectedRankingYear
      })
    }
    return () => clearScoresForCompare()
  }, [
    clearScoresForCompare,
    compare.selectedInstitutions,
    compare.selectedRankingSystem,
    compare.selectedRankingYear,
    getScoresByInstitutionIDsForCompare
  ])

  React.useEffect(() => {
    const rankingSeriesSet = new Set([
      ...compare.currentRankings.ranks.map(i => i.institution_id)
    ])
    const rankingSeries = [...rankingSeriesSet].sort()
    const currentSeries = compare.selectedInstitutions
      .map(i => parseInt(i.key))
      .sort()
    if (
      rankingSeries.every((value, index) => value === currentSeries[index]) &&
      compare.selectedInstitutions.length > 1 &&
      compare.currentRankings.ranks.length
    ) {
      const chartProps = compareRankChartProps({
        rawData: compare.currentRankings.ranks,
        categoryKey: 'year',
        seriesKey: 'institution_id',
        seriesNames: compare.selectedInstitutions.map(i => ({
          id: i.key,
          name: i.label
        }))
      })
      const alias = c.rankingSystems[compare.selectedRankingSystem].alias
      setCompareRankChart(
        <LineChart chartTitle={`Rank compare: ${alias}`} {...chartProps} />
      )
    } else {
      setCompareRankChart(null)
    }
  }, [
    compare.currentRankings.ranks,
    compare.selectedInstitutions,
    compare.selectedRankingSystem
  ])

  React.useEffect(() => {
    const rankingSeriesSet = new Set([
      ...compare.currentRankings.scores.map(i => i.institution_id)
    ])
    const rankingSeries = [...rankingSeriesSet].sort()
    const currentSeries = compare.selectedInstitutions
      .map(i => parseInt(i.key))
      .sort()
    if (
      rankingSeries.every((value, index) => value === currentSeries[index]) &&
      compare.selectedInstitutions.length > 1 &&
      compare.currentRankings.scores.length
    ) {
      const chartProps = compareScoreChartProps({
        rawData: compare.currentRankings.scores,
        seriesNames: compare.selectedInstitutions.map(i => ({
          id: i.key,
          name: i.label
        }))
      })
      const alias = c.rankingSystems[compare.selectedRankingSystem].alias
      setCompareScoreChart(
        <RadarChart
          chartTitle={`Score compare: ${alias} - ${compare.selectedRankingYear}`}
          {...chartProps}
        />
      )
    } else {
      setCompareScoreChart(null)
    }
  }, [
    compare.currentRankings.scores,
    compare.selectedInstitutions,
    compare.selectedRankingSystem,
    compare.selectedRankingYear
  ])

  return (
    <>
      <EuiFlexGroup>
        <EuiFlexItem grow={1}>
          <CompareSearch />
          <EuiSpacer />
          <SuperSelect
            key='ranking system select'
            isLoading={rankingSystems.isLoading}
            options={systems}
            onSelectChange={value => setRankingSystemForCompare(value)}
            selectedValue={compare.selectedRankingSystem}
          />
          <EuiSpacer />
          <SuperSelect
            key='ranking year select'
            isLoading={rankingSystems.isLoading}
            options={years}
            onSelectChange={value => setRankingYearForCompare(value)}
            selectedValue={compare.selectedRankingYear}
          />
        </EuiFlexItem>
        <EuiFlexItem grow={3}>{compareRankChart || noChartMessage}</EuiFlexItem>
        <EuiFlexItem grow={3}>
          {compareScoreChart || noChartMessage}
        </EuiFlexItem>
      </EuiFlexGroup>
    </>
  )
}

const mapStateToProps = state => ({
  state: {
    compare: {
      selectedInstitutions: state.compare.selectedInstitutions,
      selectedRankingSystem: state.compare.selectedRankingSystem,
      selectedRankingYear: state.compare.selectedRankingYear,
      isLoadingRanks: state.compare.isLoadingRanks,
      isLoadingScores: state.compare.isLoadingScores,
      currentRankings: state.compare.currentRankings,
      errorRankings: state.compare.errorRankings
    },
    rankingSystems: {
      isLoading: state.rankingSystems.isLoading,
      currentRankingSystems: state.rankingSystems.currentRankingSystems,
      error: state.rankingSystems.error
    }
  }
})
const mapDispatchToProps = {
  getRankingSystems: rankingSystemsActions.getRankingSystems,
  clearCurrentRankingSystems: rankingSystemsActions.clearCurrentRankingSystems,

  setInstitutionsForCompare: compareActions.setInstitutionsForCompare,
  setRankingSystemForCompare: compareActions.setRankingSystemForCompare,
  setRankingYearForCompare: compareActions.setRankingYearForCompare,

  getRanksByInstitutionIDsForCompare:
    compareActions.getRanksByInstitutionIDsForCompare,
  getScoresByInstitutionIDsForCompare:
    compareActions.getScoresByInstitutionIDsForCompare,
  clearRanksForCompare: compareActions.clearRanksForCompare,
  clearScoresForCompare: compareActions.clearScoresForCompare
}
export default connect(mapStateToProps, mapDispatchToProps)(ComparePage)
