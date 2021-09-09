import React from 'react'
import { Helmet } from 'react-helmet'
import { useLocation } from 'react-router'
import styled, { ThemeProvider } from 'styled-components'

import { AutoScrollToTop, Footer, Navbar, ScrollToTop } from '..'
import * as config from '../../config'
import '../../assets/css/index.scss'
import 'flag-icon-css/css/flag-icon.min.css'
import { r } from '../../routes'

const customTheme = {
  euiTitleColor: 'dodgerblue'
}

const StyledLayout = styled.div`
  width: 100%;
  max-width: 100vw;
  min-height: 100vh;
  background: rgb(224, 228, 234);
  display: flex;
  flex-direction: column;
`

const Layout = props => {
  const [navbarVisible, setNavbarVisible] = React.useState(true)
  const location = useLocation()

  React.useEffect(() => {
    if (
      location.pathname === '/' ||
      location.pathname.startsWith(r.rankingTable.url)
    ) {
      setNavbarVisible(false)
    } else {
      setNavbarVisible(true)
    }
  }, [location.pathname])

  return (
    <>
      <Helmet>
        <meta charSet='utf-8' />
        <title>{config.APP_NAME}</title>
        <link rel='canonical' href={config.APP_URL} />
      </Helmet>
      <ThemeProvider theme={customTheme}>
        <AutoScrollToTop />
        {navbarVisible && <Navbar />}
        <StyledLayout>{props.children}</StyledLayout>
        <ScrollToTop />
        <Footer />
      </ThemeProvider>
    </>
  )
}

export default Layout
