from backend.utils.ids import IdFactory, Id

class ObjectWithId:
    """
    Ids can be set only once. By default a default Id is generated
    by the IdFactory. If the object needs to be loaded from file it's id
    will be reset and its counterpart in the IdFactory will be rolled back.
    """
    def __init__(self):
        self._id = IdFactory.get_obj_id(self)
        self._can_be_set = True

    @property
    def id(self):
        return self._id
    
    @id.setter
    def id(self, new_id):
        """
        This setter can be called any number of times, but we allow the id to change only
        once (i.e. when the object is loaded from disk). After that if the input to this setter
        is changed, then it's a bug:
                    new_id should ALWAYS be the same as the already existing _id
        (In principle this method should only be called once anyways, so this is in place just
        for debugging).
        """
        if self._can_be_set:
            if not Id.is_id(new_id):
                raise ValueError(f"Given Id is not in a compatible format! {new_id}")
            IdFactory.roll_back_id(self,self._id)
            IdFactory.check_id_against_type(type(self),new_id)
            self._id = Id(new_id)
            self._can_be_set = False
        else:
            if new_id != self._id:
                raise ValueError("Trying to change the id to an already defined object is not allowed.")