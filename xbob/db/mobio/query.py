#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Laurent El Shafey <Laurent.El-Shafey@idiap.ch>

"""This module provides the Dataset interface allowing the user to query the
MOBIO database in the most obvious ways.
"""

import os
from bob.db import utils
from .models import *
from .driver import Interface

import xbob.db.verification.utils

SQLITE_FILE = Interface().files()[0]

class Database(xbob.db.verification.utils.SQLiteDatabase, xbob.db.verification.utils.ZTDatabase):
  """The dataset class opens and maintains a connection opened to the Database.

  It provides many different ways to probe for the characteristics of the data
  and for the data itself inside the database.
  """

  def __init__(self):
    # call base class constructors to open a session to the database
    xbob.db.verification.utils.SQLiteDatabase.__init__(self, SQLITE_FILE)
    xbob.db.verification.utils.ZTDatabase.__init__(self)

  def groups(self):
    """Returns the names of all registered groups"""

    return ProtocolPurpose.group_choices

  def genders(self):
    """Returns the list of genders"""

    return Client.gender_choices

  def subworld_names(self):
    """Returns all registered subworld names"""

    self.assert_validity()
    l = self.subworlds()
    retval = [str(k.name) for k in l]
    return retval

  def subworlds(self):
    """Returns the list of subworlds"""

    return list(self.query(Subworld))

  def has_subworld(self, name):
    """Tells if a certain subworld is available"""

    self.assert_validity()
    return self.query(Subworld).filter(Subworld.name==name).count() != 0

  def clients(self, protocol=None, groups=None, subworld=None, gender=None):
    """Returns a list of Clients for the specific query by the user.

    Keyword Parameters:

    protocol
      The protocol to consider ('male', 'female')

    groups
      The groups to which the clients belong ('dev', 'eval', 'world')
      Please note that world data are protocol/gender independent

    subworld
      Specify a split of the world data ('onethird', 'twothirds', 'twothirds-subsampled')
      In order to be considered, 'world' should be in groups and only one
      split should be specified.

    gender
      The gender to consider ('male', 'female')

    Returns: A list containing all the clients which have the given properties.
    """

    protocol = self.check_parameters_for_validity(protocol, "protocol", self.protocol_names(), [])
    groups = self.check_parameters_for_validity(groups, "group", self.groups(), [])
    subworld = self.check_parameters_for_validity(subworld, "subworld", self.subworld_names(), [])
    gender = self.check_parameters_for_validity(gender, "gender", self.genders(), [])

    # List of the clients
    q = self.query(Client)
    if protocol:
      q = q.filter(Client.gender.in_(protocol))
    if groups:
      q = q.filter(Client.sgroup.in_(groups))
    if subworld:
      q = q.join((Subworld, Client.subworld)).filter(Subworld.name.in_(subworld))
    if gender:
      q = q.filter(Client.gender.in_(gender))
    q = q.order_by(Client.id)
    return list(q)

  def has_client_id(self, id):
    """Returns True if we have a client with a certain integer identifier"""

    return self.query(Client).filter(Client.id==id).count() != 0

  def client(self, id):
    """Returns the Client object in the database given a certain id. Raises
    an error if that does not exist."""

    return self.query(Client).filter(Client.id==id).one()

  def tclients(self, protocol=None, groups=None, subworld='onethird', gender=None):
    """Returns a set of T-Norm clients for the specific query by the user.

    Keyword Parameters:

    protocol
      One of the MOBIO protocols ('male', 'female').

    groups
      Ignored.
      For the MOBIO database, this has no impact as the Z-Norm clients are coming from
      the 'world' set, and are hence the same for both the 'dev' and 'eval' sets.

    subworld
      Specify a split of the world data ('onethird', 'twothirds', 'twothirds-subsampled')
      Please note that 'onethird' is the default value.

    gender
      The gender to consider ('male', 'female')

    Returns: A list containing all the T-norm clients belonging to the given group.
    """

    return self.clients(protocol, 'world', subworld, gender)

  def zclients(self, protocol=None, groups=None, subworld='onethird', gender=None):
    """Returns a set of Z-Norm clients for the specific query by the user.

    Keyword Parameters:

    protocol
      One of the MOBIO protocols ('male', 'female').

    groups
      Ignored.
      For the MOBIO database, this has no impact as the Z-Norm clients are coming from
      the 'world' set, and are hence the same for both the 'dev' and 'eval' sets.

    subworld
      Specify a split of the world data ('onethird', 'twothirds', 'twothirds-subsampled')
      Please note that 'onethird' is the default value.

    gender
      The gender to consider ('male', 'female')

    Returns: A list containing all the Z-norm clients belonging to the given group.
    """

    return self.clients(protocol, 'world', subworld, gender)

  def models(self, protocol=None, groups=None, subworld=None, gender=None):
    """Returns a set of models for the specific query by the user.

    Keyword Parameters:

    protocol
      One of the Mobio protocols ('male', 'female').

    groups
      The groups to which the subjects attached to the models belong ('dev', 'eval', 'world')
      Please note that world data are protocol/gender independent

    subworld
      Specify a split of the world data ('onethird', 'twothirds', 'twothirds-subsampled')
      In order to be considered, 'world' should be in groups and only one
      split should be specified.

    gender
      The gender to consider ('male', 'female')

    Returns: A list containing all the models belonging to the given group.
    """

    return self.clients(protocol, groups, subworld, gender)

  def model_ids(self, protocol=None, groups=None, subworld=None, gender=None):
    """Returns a set of models ids for the specific query by the user.

    Keyword Parameters:

    protocol
      One of the Mobio protocols ('male', 'female').

    groups
      The groups to which the subjects attached to the models belong ('dev', 'eval', 'world')
      Please note that world data are protocol/gender independent

    subworld
      Specify a split of the world data ('onethird', 'twothirds', 'twothirds-subsampled')
      In order to be considered, 'world' should be in groups and only one
      split should be specified.

    gender
      The gender to consider ('male', 'female')

    Returns: A list containing the ids of all models belonging to the given group.
    """

    return [client.id for client in self.clients(protocol, groups, subworld, gender)]

  def tmodels(self, protocol=None, groups=None, subworld='onethird', gender=None):
    """Returns a set of T-Norm models for the specific query by the user.

    Keyword Parameters:

    protocol
      Ignored.

    groups
      Ignored.
      For the MOBIO database, this has no impact as the Z-Norm clients are coming from
      the 'world' set, and are hence the same for both the 'dev' and 'eval' sets.

    subworld
      Specify a split of the world data ('onethird', 'twothirds', 'twothirds-subsampled')
      Please note that 'onethird' is the default value.

    gender
      The gender to consider ('male', 'female')

    Returns: A list containing all the T-norm models belonging to the given group.
    """

    subworld = self.check_parameters_for_validity(subworld, "subworld", self.subworld_names(), [])
    gender = self.check_parameters_for_validity(gender, "gender", self.genders(), [])

    # List of the clients
    q = self.query(TModel).join(Client)
    if subworld:
      q = q.join((Subworld, Client.subworld)).filter(Subworld.name.in_(subworld))
    if gender:
      q = q.filter(Client.gender.in_(gender))
    q = q.order_by(TModel.id)
    return list(q)

  def tmodel_ids(self, protocol=None, groups=None, subworld='onethird', gender=None):
    """Returns a list of ids of T-Norm models for the specific query by the user.

    Keyword Parameters:

    protocol
      Ignored.

    groups
      Ignored.
      For the MOBIO database, this has no impact as the Z-Norm clients are coming from
      the 'world' set, and are hence the same for both the 'dev' and 'eval' sets.

    subworld
      Specify a split of the world data ('onethird', 'twothirds', 'twothirds-subsampled')
      Please note that 'onethird' is the default value.

    gender
      The gender to consider ('male', 'female')

    Returns: A list containing the ids of all T-norm models belonging to the given group.
    """
    return [tmodel.id for tmodel in self.tmodels(protocol, groups, subworld, gender)]

  def get_client_id_from_model_id(self, model_id):
    """Returns the client_id attached to the given model_id

    Keyword Parameters:

    model_id
      The model_id to consider

    Returns: The client_id attached to the given model_id
    """
    return model_id

  def objects(self, protocol=None, purposes=None, model_ids=None,
      groups=None, classes=None, subworld=None, gender=None):
    """Returns a set of Files for the specific query by the user.

    Keyword Parameters:

    protocol
      One of the MOBIO protocols ('male', 'female').

    purposes
      The purposes required to be retrieved ('enrol', 'probe') or a tuple
      with several of them. If 'None' is given (this is the default), it is
      considered the same as a tuple with all possible values. This field is
      ignored for the data from the "world" group.

    model_ids
      Only retrieves the files for the provided list of model ids (claimed
      client id).  If 'None' is given (this is the default), no filter over
      the model_ids is performed.

    groups
      One of the groups ('dev', 'eval', 'world') or a tuple with several of them.
      If 'None' is given (this is the default), it is considered the same as a
      tuple with all possible values.

    classes
      The classes (types of accesses) to be retrieved ('client', 'impostor')
      or a tuple with several of them. If 'None' is given (this is the
      default), it is considered the same as a tuple with all possible values.

    subworld
      Specify a split of the world data ('onethird', 'twothirds', 'twothirds-subsampled')
      In order to be considered, "world" should be in groups and only one
      split should be specified.

    gender
      The gender to consider ('male', 'female')

    Returns: A set of Files with the given properties.
    """

    protocol = self.check_parameters_for_validity(protocol, "protocol", self.protocol_names())
    purposes = self.check_parameters_for_validity(purposes, "purpose", self.purposes())
    groups = self.check_parameters_for_validity(groups, "group", self.groups())
    classes = self.check_parameters_for_validity(classes, "class", ('client', 'impostor'))
    subworld = self.check_parameters_for_validity(subworld, "subworld", self.subworld_names(), [])
    gender = self.check_parameters_for_validity(gender, "gender", self.genders(), [])

    import collections
    if(model_ids is None):
      model_ids = ()
    elif not isinstance(model_ids, collections.Iterable):
      model_ids = (model_ids,)

    # Now query the database
    retval = []
    if 'world' in groups:
      q = self.query(File).join(Client).filter(Client.sgroup == 'world')
      if subworld:
        q = q.join((Subworld, File.subworld)).filter(Subworld.name.in_(subworld))
      if gender:
        q = q.filter(Client.gender.in_(gender))
      if model_ids:
        q = q.filter(File.client_id.in_(model_ids))
      q = q.order_by(File.client_id, File.session_id, File.speech_type, File.shot_id, File.device)
      retval += list(q)

    if ('dev' in groups or 'eval' in groups):
      if('enrol' in purposes):
        q = self.query(File).join(Client).join((ProtocolPurpose, File.protocol_purposes)).join(Protocol).\
              filter(and_(Protocol.name.in_(protocol), ProtocolPurpose.sgroup.in_(groups), ProtocolPurpose.purpose == 'enrol'))
        if gender:
          q = q.filter(Client.gender.in_(gender))
        if model_ids:
          q = q.filter(Client.id.in_(model_ids))
        q = q.order_by(File.client_id, File.session_id, File.speech_type, File.shot_id, File.device)
        retval += list(q)

      if('probe' in purposes):
        if('client' in classes):
          q = self.query(File).join(Client).join((ProtocolPurpose, File.protocol_purposes)).join(Protocol).\
                filter(and_(Protocol.name.in_(protocol), ProtocolPurpose.sgroup.in_(groups), ProtocolPurpose.purpose == 'probe'))
          if gender:
            q = q.filter(Client.gender.in_(gender))
          if model_ids:
            q = q.filter(Client.id.in_(model_ids))
          q = q.order_by(File.client_id, File.session_id, File.speech_type, File.shot_id, File.device)
          retval += list(q)

        if('impostor' in classes):
          q = self.query(File).join(Client).join((ProtocolPurpose, File.protocol_purposes)).join(Protocol).\
                filter(and_(Protocol.name.in_(protocol), ProtocolPurpose.sgroup.in_(groups), ProtocolPurpose.purpose == 'probe'))
          if gender:
            q = q.filter(Client.gender.in_(gender))
          if len(model_ids) == 1:
            q = q.filter(not_(File.client_id.in_(model_ids)))
          q = q.order_by(File.client_id, File.session_id, File.speech_type, File.shot_id, File.device)
          retval += list(q)

    return list(set(retval)) # To remove duplicates

  def tobjects(self, protocol=None, model_ids=None, groups=None, subworld='onethird', gender=None):
    """Returns a set of filenames for enroling T-norm models for score
       normalization.

    Keyword Parameters:

    protocol
      Ignored.

    model_ids
      Only retrieves the files for the provided list of model ids.
      If 'None' is given (this is the default), no filter over
      the model_ids is performed.

    groups
      Ignored.
      For the MOBIO database, this has no impact as the Z-Norm clients are coming from
      the 'world' set, and are hence the same for both the 'dev' and 'eval' sets.

    subworld
      Specify a split of the world data ('onethird', 'twothirds', 'twothirds-subsampled')
      Please note that 'onethird' is the default value.

    gender
      The gender to consider ('male', 'female')

    Returns: A set of Files with the given properties.
    """

    subworld = self.check_parameters_for_validity(subworld, "subworld", self.subworld_names(), [])
    gender = self.check_parameters_for_validity(gender, "gender", self.genders(), [])

    if(model_ids is None):
      model_ids = ()
    elif isinstance(model_ids, (str,unicode)):
      model_ids = (model_ids,)

    # Now query the database
    retval = []
    q = self.query(File)
    if subworld:
      q = q.join((Subworld, File.subworld)).filter(Subworld.name.in_(subworld))
    q = q.join((TModel, File.tmodels))
    if model_ids:
      q = q.filter(TModel.id.in_(model_ids))
    if gender:
      q = q.join(Client).filter(Client.gender.in_(gender))
    q = q.order_by(File.client_id, File.session_id, File.speech_type, File.shot_id, File.device)
    retval += list(q)
    return retval

  def zobjects(self, protocol=None, model_ids=None, groups=None, subworld='onethird', gender=None):
    """Returns a set of Files to perform Z-norm score normalization.

    Keyword Parameters:

    protocol
      One of the MOBIO protocols ('male', 'female').

    model_ids
      Only retrieves the files for the provided list of model ids (claimed
      client id).  If 'None' is given (this is the default), no filter over
      the model_ids is performed.

    groups
      Ignored.

    subworld
      Specify a split of the world data ('onethird', 'twothirds', 'twothirds-subsampled')
      Please note that 'onethird' is the default value.

    gender
      The gender to consider ('male', 'female')

    Returns: A set of Files with the given properties.
    """

    return self.objects(protocol, None, model_ids, 'world', None, subworld, gender)

  def protocol_names(self):
    """Returns all registered protocol names"""

    l = self.protocols()
    retval = [str(k.name) for k in l]
    return retval

  def protocols(self):
    """Returns all registered protocols"""

    return list(self.query(Protocol))

  def has_protocol(self, name):
    """Tells if a certain protocol is available"""

    return self.query(Protocol).filter(Protocol.name==name).count() != 0

  def protocol(self, name):
    """Returns the protocol object in the database given a certain name. Raises
    an error if that does not exist."""

    return self.query(Protocol).filter(Protocol.name==name).one()

  def protocol_purposes(self):
    """Returns all registered protocol purposes"""

    return list(self.query(ProtocolPurpose))

  def purposes(self):
    """Returns the list of allowed purposes"""

    return ProtocolPurpose.purpose_choices

  def paths(self, ids, prefix=None, suffix=None):
    """Returns a full file paths considering particular file ids, a given
    directory and an extension

    Keyword Parameters:

    id
      The ids of the object in the database table "file". This object should be
      a python iterable (such as a tuple or list).

    prefix
      The bit of path to be prepended to the filename stem

    suffix
      The extension determines the suffix that will be appended to the filename
      stem.

    Returns a list (that may be empty) of the fully constructed paths given the
    file ids.
    """

    fobj = self.query(File).filter(File.id.in_(ids))
    retval = []
    for p in ids:
      retval.extend([k.make_path(prefix, suffix) for k in fobj if k.id == p])
    return retval

  def reverse(self, paths):
    """Reverses the lookup: from certain stems, returning file ids

    Keyword Parameters:

    paths
      The filename stems I'll query for. This object should be a python
      iterable (such as a tuple or list)

    Returns a list (that may be empty).
    """

    fobj = self.query(File).filter(File.path.in_(paths))
    retval = []
    for p in paths:
      retval.extend([k.id for k in fobj if k.path == p])
    return retval

