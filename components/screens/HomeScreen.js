// HomeScreen.js
import React from 'react';
import { View, Text, Button, Pressable } from 'react-native';

const HomeScreen = ({ navigation }) => {
  return (
    <View>
      <Text>Welcome to the Home Screen!</Text>
      <Button
        title="Go to Group List"
        onPress={() => navigation.navigate('GroupList')}
      />
    </View>
  );
};

export default HomeScreen;
