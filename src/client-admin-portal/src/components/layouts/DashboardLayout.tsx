import React from 'react'

interface Props {
  children: React.ReactNode;
}

const DashboardLayout = ({ children }: Props) => {
  return (
    <>
      <p>navbar</p>
      <p>sidebar</p>
      {children}

    </>

  )
}

export default DashboardLayout