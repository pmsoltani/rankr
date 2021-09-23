import React from 'react'
import { Helmet } from 'react-helmet'
import { useLocation } from 'react-router'
import styled, { ThemeProvider } from 'styled-components'

import { AutoScrollToTop, Footer, Navbar, ScrollToTop } from '..'
import { appLogo } from '../../assets/images'
import * as c from '../../config'
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
        <title>{c.FRONTEND_NAME}</title>
        <meta name='description' content={c.FRONTEND_DESCRIPTION} />
        <html lang='en-US' />
        <meta property='og:title' content={c.FRONTEND_NAME} />
        <meta property='og:image' content={appLogo} />
        <base target='_blank' href={c.FRONTEND_URL} />
        <link rel='canonical' href={c.FRONTEND_URL} />
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
