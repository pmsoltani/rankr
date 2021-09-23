import React from 'react'
import { Helmet } from 'react-helmet'
import axios from 'axios'
import {
  EuiMarkdownFormat,
  EuiPage,
  EuiPageBody,
  EuiPageContent,
  EuiPageContentBody
} from '@elastic/eui'

import aboutPageContents from './about.md'
import * as c from '../../config'
import { r } from '../../routes'
import { formatURL } from '../../utils'

const AboutPage = props => {
  const [content, setContent] = React.useState(null)
  React.useEffect(() => {
    axios
      .get(aboutPageContents)
      .then(res => res.data)
      .then(text => setContent(text))
  })

  return (
    <>
      <Helmet>
        <title>{`${c.FRONTEND_NAME}: About`}</title>
        <meta name='description' content={`About ${c.FRONTEND_NAME}`} />
        <meta property='og:title' content={`${c.FRONTEND_NAME}: About`} />
        <link rel='canonical' href={formatURL(`${r.about.url}`, [], false)} />
      </Helmet>
      <EuiPage>
        <EuiPageBody component='section'>
          <EuiPageContent borderRadius='none' hasShadow={false}>
            <EuiPageContentBody restrictWidth={800}>
              <EuiMarkdownFormat>{content}</EuiMarkdownFormat>
            </EuiPageContentBody>
          </EuiPageContent>
        </EuiPageBody>
      </EuiPage>
    </>
  )
}

export default AboutPage
