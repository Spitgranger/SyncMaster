import * as React from 'react';
import { styled, useTheme } from '@mui/material/styles';
import Grid from '@mui/material/Grid2';
import Box from '@mui/material/Box';
import Drawer from '@mui/material/Drawer';
import MuiAppBar, { AppBarProps as MuiAppBarProps } from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import List from '@mui/material/List';
import Typography from '@mui/material/Typography';
import Divider from '@mui/material/Divider';
import IconButton from '@mui/material/IconButton';
import MenuIcon from '@mui/icons-material/Menu';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import Image from 'next/image';
import hamiltonLogo from "../../../public/hamiltonCityLogo.svg";
import { Apartment, Settings, Business } from '@mui/icons-material';
import { AiOutlineGlobal } from 'react-icons/ai';
import SpecificIcon from '../Icons/SpecificIcon';
import UserIcon from '../Icons/UserIcon';
import { Avatar } from '@mui/material';
import { useRouter } from 'next/router';
interface Props {
  children: React.ReactNode;
}

const drawerWidth = 248;

const Main = styled('main', { shouldForwardProp: (prop) => prop !== 'open' })<{
  open?: boolean;
}>(({ theme }) => ({
  flexGrow: 1,
  padding: `${theme.spacing(3)} 0`,
  transition: theme.transitions.create('margin', {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.leavingScreen,
  }),
  marginLeft: `-${drawerWidth}px`,
  variants: [
    {
      props: ({ open }) => open,
      style: {
        transition: theme.transitions.create('margin', {
          easing: theme.transitions.easing.easeOut,
          duration: theme.transitions.duration.enteringScreen,
        }),
        marginLeft: 0,
      },
    },
  ],
}));

interface AppBarProps extends MuiAppBarProps {
  open?: boolean;
}

const AppBar = styled(MuiAppBar, {
  shouldForwardProp: (prop) => prop !== 'open',
})<AppBarProps>(({ theme }) => ({
  transition: theme.transitions.create(['margin', 'width'], {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.leavingScreen,
  }),
  justifyContent: "center",
  backgroundColor: "#fff",
  boxShadow: "none",
  color: "black",
  borderBottom: `1px solid ${theme.palette.divider}`,
  variants: [
    {
      props: ({ open }) => open,
      style: {
        width: `calc(100% - ${drawerWidth}px)`,
        marginLeft: `${drawerWidth}px`,
        transition: theme.transitions.create(['margin', 'width'], {
          easing: theme.transitions.easing.easeOut,
          duration: theme.transitions.duration.enteringScreen,
        }),
      },
    },
  ],
}));

const DrawerHeader = styled('div')(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  padding: theme.spacing(0, 1),
  ...theme.mixins.toolbar,
  justifyContent: 'flex-end',
}));

interface SidebarLink {
  text: string;
  icon: React.JSX.Element;
  route: string;
}

export default function DashboardLayout({ children }: Props) {
  const theme = useTheme();
  const [open, setOpen] = React.useState(false);
  const router = useRouter();

  const handleDrawerOpen = () => {
    setOpen((open) => !open);
  };

  const handleDrawerClose = () => {
    setOpen(false);
  };

  return (
    <>
      <AppBar position="fixed">
        <Toolbar sx={{ display: "flex", justifyContent: "space-between" }}>
          <Grid container alignItems={"center"}>
            <IconButton
              color="inherit"
              aria-label="open drawer"
              onClick={handleDrawerOpen}
              edge="start"
              sx={{
                mr: 2,
              }}
            >
              <MenuIcon />
            </IconButton>
            <Grid container spacing={1} width={"168px"} display={"flex"} flexDirection={"row"}>
              <Image src={hamiltonLogo} width={44.71} height={38} alt='Hamilton Logo' />

              <Typography width={115} variant="body1" lineHeight={1.2} fontWeight={700} >
                Hamilton Waterworks
              </Typography>
            </Grid>
          </Grid>
          <Avatar />
        </Toolbar>
      </AppBar>
      <Box sx={{ display: 'flex' }}>
        <Drawer
          sx={{
            width: drawerWidth,
            flexShrink: 0,
            '& .MuiDrawer-paper': {
              width: drawerWidth,
              boxSizing: 'border-box',
            },
          }}
          variant="persistent"
          anchor="left"
          open={open}
        >
          <DrawerHeader>
            <IconButton onClick={handleDrawerClose}>
              {theme.direction === 'ltr' ? <ChevronLeftIcon /> : <ChevronRightIcon />}
            </IconButton>
          </DrawerHeader>
          <Divider />
          <Typography pt={1} px={2} variant='subtitle1' color="textSecondary">Documents</Typography>
          <List>
            {[{ text: 'Site Wide', icon: <AiOutlineGlobal color='black' size={24} />, route: "/dashboard/sitewide" }, { text: 'Site Specific', icon: <SpecificIcon />, route: "/dashboard/sitespecific" }].map((link: SidebarLink) => (
              <ListItem key={link.text} disablePadding>
                <ListItemButton onClick={() => { router.push(link.route) }} selected={router.pathname.startsWith(link.route)}>
                  <ListItemIcon >
                    {link.icon}
                  </ListItemIcon>
                  <ListItemText primary={link.text} />
                </ListItemButton>
              </ListItem>
            ))}
          </List>
          <Divider />
          <Typography pt={1} px={2} variant='subtitle1' color="textSecondary">Organization</Typography>
          <List>
            {[{ text: 'Site Visits', icon: <Business sx={{ color: "black" }} />, route: "/dashboard/sitevisits" }, { text: 'Manage Sites', icon: <Apartment sx={{ color: "black" }} />, route: "/dashboard/managesites" }, { text: 'Manage Users', icon: <UserIcon />, route: "/dashboard/manageusers" }, { text: 'Settings', icon: <Settings sx={{ color: "black" }} />, route: "/dashboard/settings" }].map((link: SidebarLink) => (
              <ListItem key={link.text} disablePadding>
                <ListItemButton onClick={() => { router.push(link.route) }} selected={router.pathname.startsWith(link.route)}>
                  <ListItemIcon>
                    {link.icon}
                  </ListItemIcon>
                  <ListItemText primary={link.text} />
                </ListItemButton>
              </ListItem>
            ))}
          </List>
        </Drawer>
        <Main open={open}>
          <DrawerHeader />
          {children}
        </Main>
      </Box>
    </>
  );
}
