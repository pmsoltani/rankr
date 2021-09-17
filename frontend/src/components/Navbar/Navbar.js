import React from 'react'
import { EuiHeader, EuiHeaderSection, EuiHeaderSectionItem } from '@elastic/eui'

import { Search, StyledLink } from '..'
import { r } from '../../routes'
import { appLogo } from '../../assets/images'
import { useWindowDimensions } from '../../hooks'

const renderLogo = () => (
  <StyledLink to={r.home.url}>
    <img
      src={appLogo}
      alt='rankr logo'
      style={{ height: 36, marginTop: '0px' }}
    />
  </StyledLink>
)

const Navbar = props => {
  const { width } = useWindowDimensions()

  return (
    <EuiHeader>
      <EuiHeaderSection grow={false}>
        <EuiHeaderSectionItem
          style={{
            display: width >= 1200 ? 'flex' : 'none',
            width: width >= 1200 ? (width - 1200) / 2 : 0
          }}
        />
        <EuiHeaderSectionItem>{renderLogo()}</EuiHeaderSectionItem>
      </EuiHeaderSection>

      <EuiHeaderSection side='right'>
        <EuiHeaderSectionItem>
          <Search />
        </EuiHeaderSectionItem>
        <EuiHeaderSectionItem
          style={{
            display: width >= 1200 ? 'flex' : 'none',
            width: width >= 1200 ? (width - 1200) / 2 : 0
          }}
        />
      </EuiHeaderSection>
    </EuiHeader>
  )
}

export default Navbar
