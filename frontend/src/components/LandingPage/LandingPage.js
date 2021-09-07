import React from 'react'

import {
  EuiPage,
  EuiPageBody,
  EuiPageContent,
  EuiFlexGroup,
  EuiFlexItem,
  EuiPageContentBody
} from '@elastic/eui'
import styled from 'styled-components'

import { RankingTableCard } from '..'

const StyledEuiPage = styled(EuiPage)`
  flex: 1;
`

const StyledEuiPageContentBody = styled(EuiPageContentBody)`
  max-width: 600px;
  & > img {
    width: 100%;
    border-radius: 50%;
  }
`

const LandingPage = props => {
  return (
    <StyledEuiPage>
      <EuiPageBody component='section'>
        <EuiFlexGroup>
          <EuiFlexItem grow={2}>
            <EuiPageContent
              horizontalPosition='center'
              verticalPosition='center'
            >
              <StyledEuiPageContentBody>
                <RankingTableCard />
              </StyledEuiPageContentBody>
            </EuiPageContent>
          </EuiFlexItem>
        </EuiFlexGroup>
      </EuiPageBody>
    </StyledEuiPage>
  )
}

export default LandingPage
