import React from 'react'
import axios from 'axios'
import {
  EuiMarkdownFormat,
  EuiPage,
  EuiPageBody,
  EuiPageContent,
  EuiPageContentBody
} from '@elastic/eui'

import aboutPageContents from './about.md'

const AboutPage = props => {
  const [content, setContent] = React.useState(null)
  React.useEffect(() => {
    axios.get(aboutPageContents)
      .then(res => res.data)
      .then(text => setContent(text))
  })

  return (
    <EuiPage>
      <EuiPageBody component='section'>
        <EuiPageContent borderRadius='none' hasShadow={false}>
          <EuiPageContentBody>
            <EuiMarkdownFormat>{content}</EuiMarkdownFormat>
          </EuiPageContentBody>
        </EuiPageContent>
      </EuiPageBody>
    </EuiPage>
  )
}

export default AboutPage
