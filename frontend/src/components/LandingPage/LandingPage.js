import React from 'react'
import { Link } from 'react-router-dom'
import {
  EuiPage,
  EuiPageBody,
  EuiPageContent,
  EuiFlexGroup,
  EuiFlexItem,
  EuiPageContentBody,
  EuiButton,
  EuiSpacer
} from '@elastic/eui'
import styled from 'styled-components'

import { r } from '../../routes'
import { landing } from '../../assets/images'

const StyledEuiPage = styled(EuiPage)`
  flex: 1;
`

const StyledEuiPageContentBody = styled(EuiPageContentBody)`
  max-width: 400px;
  max-height: 400px;
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
                <img src={landing} alt='charts' />
              </StyledEuiPageContentBody>
              <EuiSpacer />
              <EuiFlexGroup justifyContent='center'>
                <Link to={r.institutions.url}>
                  <EuiButton color='primary' fill>
                    Get started
                  </EuiButton>
                </Link>
              </EuiFlexGroup>
            </EuiPageContent>
          </EuiFlexItem>
        </EuiFlexGroup>
      </EuiPageBody>
    </StyledEuiPage>
  )
}

export default LandingPage
