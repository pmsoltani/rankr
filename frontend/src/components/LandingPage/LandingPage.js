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

const LandingPage = props => {
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
                <RankingTableCard />
              </EuiPageContentBody>
            </EuiPageContent>
          </EuiFlexItem>
        </EuiFlexGroup>
      </EuiPageBody>
    </StyledEuiPage>
  )
}

export default LandingPage
