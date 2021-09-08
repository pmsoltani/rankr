import React from 'react'
import { useLocation } from 'react-router-dom'

const AutoScrollToTop = props => {
  const { pathname } = useLocation()
  React.useEffect(() => window.scrollTo(0, 0), [pathname])
  return null
}

export default AutoScrollToTop
