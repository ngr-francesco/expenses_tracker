// AppNavigator.js
import React from 'react';
import { createStackNavigator } from '@react-navigation/stack';
import { NavigationContainer } from '@react-navigation/native';
import HomeScreen from './screens/HomeScreen';
import GroupListScreen from './screens/GroupListScreen';
import GroupPage from './screens/GroupPage';

const Stack = createStackNavigator();

const AppNavigator = () => {
  return (
    <NavigationContainer>
      <Stack.Navigator initialRouteName="Home">
        <Stack.Screen name="Home" component={HomeScreen} />
        <Stack.Screen name="GroupList" component={GroupListScreen} />
        <Stack.Screen name='GroupPage' component={GroupPage} />
      </Stack.Navigator>
    </NavigationContainer>
  );
};

export default AppNavigator;
