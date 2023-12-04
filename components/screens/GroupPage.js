// GroupListScreen.js
import React, { useState, useEffect } from 'react';
import { View, Text, FlatList, TouchableOpacity } from 'react-native';
import { useRoute } from '@react-navigation/native';

const GroupPage = () => {
    const route = useRoute()
    const params = route.params
    console.log("Received params", params.id)
    
    
    return (
        <View>
          <Text>This is the page for group {params.name}</Text>
          <Text>Group ID: {params.id}</Text>
          <Text>Group members: {params.members.join(', ')}</Text>
          {/* Display more information based on the parameters */}
        </View>
      );
}

export default GroupPage