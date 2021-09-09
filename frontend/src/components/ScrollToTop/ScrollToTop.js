import React from 'react'
import { EuiIcon } from '@elastic/eui'

const ScrollToTop = props => {
  const [isVisible, setIsVisible] = React.useState(false)
  const scrollToTop = () => window.scrollTo({ top: 0, behavior: 'smooth' })

  React.useEffect(() => {
    const toggleVisibility = () => {
      window.pageYOffset > 300 ? setIsVisible(true) : setIsVisible(false)
    }
    window.addEventListener('scroll', toggleVisibility)
    return () => window.removeEventListener('scroll', toggleVisibility)
  }, [])

  return (
    <>
      {isVisible && (
        <div id='scroll-to-top' onClick={scrollToTop}>
          <EuiIcon color='white' size='xl' type='arrowUp' />
        </div>
      )}
    </>
  )
}

export default ScrollToTop
