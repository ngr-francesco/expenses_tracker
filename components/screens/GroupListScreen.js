// GroupListScreen.js
import React, { useState, useEffect } from 'react';
import { View, Text, FlatList, TouchableOpacity } from 'react-native';
import { useNavigation } from '@react-navigation/native';

const GroupListScreen = () => {
  const [groups, setGroups] = useState([]);
  const navigation = useNavigation();

  useEffect(() => {
    const fetchGroups = async () => {
      try{
        const data = require('../../usr_data/groups_list.json');
        console.log(data);
        console.log(data[0].name)
        setGroups(data)
      }catch (error) {
        console.error("Error loading group data:", error)
      }
    };
  
    fetchGroups();
  }, []);

  const handlePress = (item) => {
    console.log("Item to send:", item)
    navigation.navigate('GroupPage', item)
  };


  return (
    <View>
      <Text>Group List</Text>
      {groups.length === 0 ? (
        <Text>Loading...</Text>
      ) : (
        <FlatList data={groups}
          keyExtractor={(item) => item.id.toString()}
          renderItem={({ item }) => (
            <TouchableOpacity 
            onPress={() => handlePress(item)}>
            <Text>{item.name}</Text>
          </TouchableOpacity>
          )}
        />
      )}
    </View>
  );
};

export default GroupListScreen;
