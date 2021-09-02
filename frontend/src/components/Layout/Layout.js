import React from 'react'
import { Helmet } from 'react-helmet'
import styled, { ThemeProvider } from 'styled-components'

import { Navbar } from '..'
import * as config from '../../config'
import '../../assets/css/index.scss'

const customTheme = {
  euiTitleColor: 'dodgerblue',
  euiFontFamily: 'Sahel'
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
  return (
    <>
      <Helmet>
        <meta charSet='utf-8' />
        <title>{config.APP_NAME}</title>
        <link rel='canonical' href={config.APP_URL} />
      </Helmet>
      <ThemeProvider theme={customTheme}>
        <Navbar />
        <StyledLayout>{props.children}</StyledLayout>
      </ThemeProvider>
    </>
  )
}

export default Layout