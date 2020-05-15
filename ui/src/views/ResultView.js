import React from 'react';
import Button from '@material-ui/core/Button';
import CssBaseline from '@material-ui/core/CssBaseline';
import Typography from '@material-ui/core/Typography';
import { makeStyles } from '@material-ui/core/styles';
import Container from '@material-ui/core/Container';
import { Select, MenuItem, TextField, Grid } from '@material-ui/core';
import {
  selectPlaylists
} from '../store/user';
import { useSelector, useDispatch } from 'react-redux';
import PlaylistView from './PlaylistView';
import PlaylistCard from '../components/PlaylistCard'

const useStyles = makeStyles((theme) => ({
    paper: {
        marginTop: theme.spacing(8),
        display: 'flex',
        flexDirection: 'row',
        alignItems: 'center',
        flexWrap: 'wrap',
        alignItems: 'center',
        boxAlign: 'center'
    }
}));

export default function ResultView() {
    const classes = useStyles();
    return (
        <div>
        <Container maxWidth="xs">
            <PlaylistView />
            <CssBaseline />
        </Container>
        <div className={classes.paper}>
            <PlaylistCard />
            <PlaylistCard />
            <PlaylistCard />
            <PlaylistCard />
            <PlaylistCard />
            <PlaylistCard />
            <PlaylistCard />
        </div>
        </div>
    )
}