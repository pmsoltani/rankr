import React from 'react'
import { EuiHeader, EuiHeaderSection, EuiHeaderSectionItem } from '@elastic/eui'

import { Search, StyledLink } from '..'
import { r } from '../../routes'
import { logo } from '../../assets/images'

const renderLogo = () => (
  <StyledLink to={r.home.url}>
    <img
      src={logo}
      alt='rankr logo'
      style={{ height: 36, margin: '4px 12px 0px' }}
    />
  </StyledLink>
)

const Navbar = props => {
  return (
    <EuiHeader>
      <EuiHeaderSection grow={false}>
        <EuiHeaderSectionItem>{renderLogo()}</EuiHeaderSectionItem>
      </EuiHeaderSection>

      <EuiHeaderSection side='right'>
        <EuiHeaderSectionItem>
          <Search />
        </EuiHeaderSectionItem>
      </EuiHeaderSection>
    </EuiHeader>
  )
}

export default Navbar
