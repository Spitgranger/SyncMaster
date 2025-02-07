import * as React from 'react';
import Head from 'next/head';
import { AppProps } from 'next/app';
import { AppCacheProvider } from '@mui/material-nextjs/v15-pagesRouter';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import theme from '@/theme';
import { NextPage } from 'next';

type NextPageWithLayout = NextPage & {
  getLayout?: (page: React.ReactElement) => React.ReactNode;
};

type AppPropsWithLayout = AppProps & {
  Component: NextPageWithLayout;
};

export default function MyApp(props: AppPropsWithLayout) {
  const { Component, pageProps } = props;
  const getLayout = Component.getLayout ?? ((page) => page)
  const layout = getLayout(<Component {...pageProps} />)

  return (
    <AppCacheProvider {...props}>
      <Head>
        <meta name="viewport" content="initial-scale=1, width=device-width" />
      </Head>
      <ThemeProvider theme={theme}>
        {/* CssBaseline kickstart an elegant, consistent, and simple baseline to build upon. */}
        <CssBaseline />
        {layout}
      </ThemeProvider>
    </AppCacheProvider>
  );
}