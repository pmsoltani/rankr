import React from 'react'
import { connect } from 'react-redux'
import { useParams } from 'react-router-dom'

import {
  EuiPage,
  EuiPageContent,
  EuiPageBody,
  EuiPageContentBody,
  EuiSpacer,
  EuiStat,
  EuiTab,
  EuiTabs,
  EuiText
} from '@elastic/eui'

import '../../types'
import {
  BarChart,
  InstitutionPageHeader,
  LineChart,
  LoadingPage,
  NotFoundPage,
  YearRange
} from '..'
import {
  institutionActions,
  rankingActions,
  wikiActions
} from '../../redux/reducers'
import { institutionStats, rankChartProps, scoreChartProps } from '../../utils'

const InstitutionPage = props => {
  /** @type {{
    currentInstitutions: Array.<Institution>, isLoading: boolean, error: any
  }} */
  const institutions = props.state.institutions
  /** @type {{
    currentRankings: {ranks: Array.<Ranking>, scores: Array.<Ranking>},
    isLoading: boolean,
    error: any
  }} */
  const rankings = props.state.rankings
  /** @type {{currentWikiPage: string, isLoading: boolean, error: any}} */
  const wiki = props.state.wiki
  const {
    getInstitutionByID,
    clearCurrentInstitutions,
    getRanksByInstitutionID,
    getScoresByInstitutionID,
    clearCurrentRankings,
    getWikiPage,
    clearCurrentWikiPage
  } = props

  /** @type {Institution|null} */
  const initialInst = null
  const [inst, setInst] = React.useState(initialInst)

  const [instStats, setInstStats] = React.useState(null)
  const tabs = [
    { id: 'overview', name: 'Overview' },
    { id: 'ranks', name: 'Ranks' },
    { id: 'scores', name: 'Scores' },
    { id: 'compare', name: 'Compare' }
  ]
  const [selectedTabID, setSelectedTabID] = React.useState('overview')
  const [rankChart, setRankChart] = React.useState(null)
  const [scoreChart, setScoreChart] = React.useState(null)
  const [pageContent, setPageContent] = React.useState(null)
  const [scoreYear, setScoreYear] = React.useState(null)
  const [slider, setSlider] = React.useState(null)
  const onYearChange = e => setScoreYear(parseInt(e.target.value))
  const onSelectedTabChanged = id => setSelectedTabID(id)
  const { institutionID } = useParams()

  React.useEffect(() => {
    if (institutionID) {
      getInstitutionByID({ institutionID })
      setSelectedTabID('ranks') // TODO: change to overview
    }
    return () => clearCurrentInstitutions()
  }, [institutionID, getInstitutionByID, clearCurrentInstitutions])

  React.useEffect(() => {
    if (institutions.currentInstitutions.length) {
      setInst(institutions.currentInstitutions[0])
    }
    return () => setInst(null)
  }, [institutions.currentInstitutions])

  React.useEffect(() => {
    if (inst) {
      setInstStats(
        institutionStats(inst.stats).map(i => (
          <EuiStat key='' {...i} titleSize='s' />
        ))
      )
    }
  }, [inst])

  React.useEffect(() => {
    if (inst) {
      const wikiURL = inst.links.find(link => link.type === 'wikipedia')?.link
      if (wikiURL) getWikiPage({ url: wikiURL })
    }
    return () => clearCurrentWikiPage()
  }, [inst, getWikiPage, clearCurrentWikiPage])

  React.useEffect(() => {
    if (inst) getRanksByInstitutionID({ institution_id: inst.id })
    return () => clearCurrentRankings()
  }, [inst, getRanksByInstitutionID, clearCurrentRankings])

  React.useEffect(() => {
    if (inst) getScoresByInstitutionID({ institution_id: inst.id })
    return () => clearCurrentRankings()
  }, [inst, getScoresByInstitutionID, clearCurrentRankings])

  React.useEffect(() => {
    if (rankings.currentRankings.ranks.length) {
      const chartProps = rankChartProps(rankings.currentRankings.ranks)
      setRankChart(<LineChart chartTitle='Rank' {...chartProps} />)
    }
  }, [rankings.currentRankings.ranks])

  React.useEffect(() => {
    if (rankings.currentRankings.scores.length) {
      const years = new Set(rankings.currentRankings.scores.map(i => i.year))
      if (!scoreYear) setScoreYear(Math.max(...years))
      const chartProps = scoreChartProps(rankings.currentRankings.scores, {
        year: scoreYear
      })
      setSlider(
        <YearRange years={years} value={scoreYear} onChange={onYearChange} />
      )
      setScoreChart(
        <BarChart chartTitle={`Scores for ${scoreYear}`} {...chartProps} />
      )
    }
  }, [scoreYear, rankings.currentRankings.scores])

  React.useEffect(() => {
    if (selectedTabID === 'overview' && wiki.isLoading) {
      setPageContent(<LoadingPage />)
    }
    if (selectedTabID === 'overview' && wiki.currentWikiPage) {
      setPageContent(wiki.currentWikiPage)
    }
  }, [selectedTabID, wiki.isLoading, wiki.currentWikiPage])

  React.useEffect(() => {
    if (selectedTabID === 'ranks' && rankings.isLoading) {
      setPageContent(<LoadingPage />)
    }
    if (selectedTabID === 'ranks') setPageContent(rankChart)
  }, [rankChart, rankings.isLoading, selectedTabID])

  React.useEffect(() => {
    if (selectedTabID === 'scores' && rankings.isLoading) {
      setPageContent(<LoadingPage />)
    }
    if (selectedTabID === 'scores') {
      setPageContent(
        <>
          {slider}
          <EuiSpacer />
          {scoreChart}
        </>
      )
    }
  }, [
    rankings.isLoading,
    rankings.currentRankings.scores,
    scoreChart,
    selectedTabID,
    slider
  ])

  React.useEffect(() => {
    if (selectedTabID === 'compare') {
      setPageContent(<EuiText>Comming soon!</EuiText>)
    }
  })

  const renderTabs = props => {
    return tabs.map((tab, index) => (
      <EuiTab
        {...(tab.href && { href: tab.href, target: '_blank' })}
        onClick={() => onSelectedTabChanged(tab.id)}
        isSelected={tab.id === selectedTabID}
        disabled={tab.disabled}
        key={index}
      >
        {tab.name}
      </EuiTab>
    ))
  }

  if (institutions.error) return <NotFoundPage />
  if (institutions.isLoading || !inst || !instStats) return <LoadingPage />

  return (
    <EuiPage>
      <EuiPageBody component='section'>
        <InstitutionPageHeader institution={inst} rightSideItems={instStats} />
        <EuiTabs size='l'>{renderTabs()}</EuiTabs>
        <EuiPageContent borderRadius='none' hasShadow={false}>
          <EuiPageContentBody>{pageContent}</EuiPageContentBody>
        </EuiPageContent>
      </EuiPageBody>
    </EuiPage>
  )
}

const mapStateToProps = state => ({
  state: {
    institutions: {
      isLoading: state.institutions.isLoading,
      currentInstitutions: state.institutions.currentInstitutions,
      selectedInstitutions: state.institutions.selectedInstitutions,
      error: state.institutions.error
    },
    rankings: {
      isLoading: state.rankings.isLoading,
      currentRankings: state.rankings.currentRankings,
      error: state.rankings.error
    },
    wiki: {
      isLoading: state.wiki.isLoading,
      currentWikiPage: state.wiki.currentWikiPage,
      error: state.wiki.error
    }
  }
})
const mapDispatchToProps = {
  getInstitutionByID: institutionActions.getInstitutionByID,
  clearCurrentInstitutions: institutionActions.clearCurrentInstitutions,
  getRanksByInstitutionID: rankingActions.getRanksByInstitutionID,
  getScoresByInstitutionID: rankingActions.getScoresByInstitutionID,
  clearCurrentRankings: rankingActions.clearCurrentRankings,
  getWikiPage: wikiActions.getWikiPage,
  clearCurrentWikiPage: wikiActions.clearCurrentWikiPage
}
export default connect(mapStateToProps, mapDispatchToProps)(InstitutionPage)
