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
import { rankrLogo } from '../../assets/images'

const StyledEuiPage = styled(EuiPage)`
  flex: 1;
`

const LandingPage = props => {
  const { rankingSystem = '', year = '' } = useParams()
  return (
    <StyledEuiPage>
      <EuiPageBody component='section'>
        <EuiFlexGroup>
          <EuiFlexItem grow={2}>
            <EuiPageContent
              color='transparent'
              horizontalPosition='center'
              verticalPosition='center'
            >
              <EuiPageContentBody restrictWidth='1000px'>
                <EuiFlexGroup justifyContent='center'>
                  <EuiFlexItem
                    style={{ display: 'flex', justifyContent: 'center' }}
                  >
                    <img
                      src={rankrLogo}
                      alt='rankr logo'
                      style={{ width: 600, margin: 'auto' }}
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
                    <RankingTableCard
                      rankingSystem={rankingSystem}
                      year={year}
                    />
                  </EuiFlexItem>
                </EuiFlexGroup>
              </EuiPageContentBody>
            </EuiPageContent>
          </EuiFlexItem>
        </EuiFlexGroup>
      </EuiPageBody>
    </StyledEuiPage>
  )
}

export default LandingPage
