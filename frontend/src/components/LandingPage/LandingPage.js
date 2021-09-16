import React from 'react'
import { useParams } from 'react-router'
import {
  EuiPage,
  EuiPageBody,
  EuiPageContent,
  EuiFlexGroup,
  EuiFlexItem,
  EuiPageContentBody,
  EuiSpacer
} from '@elastic/eui'
import styled from 'styled-components'

import { RankingTableCard, SiteSearch } from '..'
import { appLogo } from '../../assets/images'

const StyledEuiPage = styled(EuiPage)`
  flex: 1;
`

const LandingPage = props => {
  const { rankingSystem = '', year = '' } = useParams()
  return (
    <StyledEuiPage>
      <EuiPageBody component='section'>
        <EuiPageContent
          color='transparent'
          horizontalPosition='center'
          verticalPosition='center'
        >
          <EuiPageContentBody restrictWidth='1200px'>
            <EuiFlexGroup justifyContent='center'>
              <EuiFlexItem
                style={{ display: 'flex', justifyContent: 'center' }}
              >
                <img
                  src={appLogo}
                  alt='rankr logo'
                  style={{ width: '30%', margin: 'auto' }}
                />
              </EuiFlexItem>
            </EuiFlexGroup>
            <EuiSpacer />
            <EuiFlexGroup justifyContent='center'>
              <EuiFlexItem>
                <SiteSearch />
              </EuiFlexItem>
            </EuiFlexGroup>
            <EuiSpacer />
            <EuiFlexGroup justifyContent='center'>
              <EuiFlexItem>
                <RankingTableCard rankingSystem={rankingSystem} year={year} />
              </EuiFlexItem>
            </EuiFlexGroup>
          </EuiPageContentBody>
        </EuiPageContent>
      </EuiPageBody>
    </StyledEuiPage>
  )
}

export default LandingPage
