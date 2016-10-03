"""
A script to generate a serialized project description for build script generation.
"""
import os
import glob
import json
from compiler_configurations.py import *

def serialize( state ):
  with open (".metaconfigure/description.json", "w") as json_file:
    subprojects = state.pop('subprojects')
    project_path = state.pop('project_path')
    implementation_extensions = state.pop('implementation_extensions')
    header_extensions = state.pop('header_extensions')
    json_file.write( json.dumps( state, indent=0 ) )
    state['subprojects'] = subprojects
    state['project_path'] = project_path
    state['implementation_extensions'] = implementation_extensions
    state['header_extensions'] = header_extensions
    
def deserialize():
  with open (".metaconfigure/description.json", "r") as json_file:
    state = json.loads( json_file.read() )
    state['subprojects'] = {}
    state['project_path'] = os.getcwd()
    set_extensions( state )
    return state

def collect_subprojects( state ):
  if os.path.isdir( os.path.join( os.getcwd(), 'dependencies' ) ):
    os.chdir('dependencies')
    root = os.getcwd()
    for name in os.listdir( os.getcwd() ) :
      if os.path.isdir( os.path.join( os.getcwd(), name ) ) :
        os.chdir( os.path.join( state['project_path'], 'subprojects', name ) )
        subproject = deserialize()
        collect_subprojects( subproject )
        state['subprojects'][name] = subproject
        os.chdir( root )
    os.chdir('..')

def reconstruct_dependency_graph( state ):
  dependencies = { state['name'] : state['subprojects'].keys() }
  for name in state['subprojects'].keys():
    dependencies.update( reconstruct_dependency_graph( state['subprojects'][name] ) )
  return dependencies

def reconstruct_build_queue( state ):
  queue = []
  graph = reconstruct_dependency_graph( state )
  while len( graph ) > 0:
    found_next = False
    next_node = None
    for node, edges in graph.items():
      queueable = True
      for edge in edges:
        if not edge in queue :
          queueable = False
          break
      if queueable:
      	next_node = node
      	found_next = True
      	break
    if not found_next:
      raise RuntimeError('Cyclic Dependencies?!')
    else:
      queue.append(next_node)
      graph.pop(next_node)
  return queue

def set_extensions( state ) :
  state['implementation_extensions'] = implementation_extensions[ state['language'] ]
  state['header_extensions'] = header_extensions[ state['language'] ]

def relative_path( state ):
  return os.path.relpath( os.getcwd(), state['project_path'] )
  
def implementation_files( state ):
  path = relative_path( state )
  files = []
  for extension in state['implementation_extensions'] :
    filenames = glob.glob( '*.' + extension )
    file_paths = [ os.path.join( path, filename ) for filename in filenames ]
    files.extend( file_paths )
  return files

def header_files( state ):
  path = relative_path( state )
  files = []
  for extension in state['header_extensions'] :
    filenames = glob.glob( '*.' + extension )
    file_paths = [ os.path.join( path, filename ) for filename in filenames ]
    files.extend( file_paths )
  return files  

def evaluate_test_leaf( state ):
  os.chdir('test')
  name = os.path.split( os.path.split( os.getcwd() )[0] )[1]
  state['unit_tests'][name] = implementation_files( state )
  os.chdir('..')

def evaluate_src_leaf( state ):
  os.chdir('src')
  state['header_files'].extend( header_files( state ) )
  state['implementation_files'].extend( implementation_files( state ) )
  os.chdir('..')

def evaluate_branch( state ):
  state['header_files'].extend( header_files( state ) )
  for name in os.listdir( os.getcwd() ):
    if os.path.isdir( os.path.join( os.getcwd(), name ) ):
      if name == 'test':
        evaluate_test_leaf( state )
      elif name == 'src' :
        evaluate_src_leaf( state )
      else :
        os.chdir( name )
        evaluate_branch( state )
  os.chdir('..')

def generate( project_name,
              project_type,
              language,
              project_version,
              is_external_project = False,
              **kwargs ):

  state = { 'name' : project_name,
            'version' : project_version,
            'type' : project_type,
            'language' : language,
            'header_files' : [],
            'implementation_files' : [],
            'unit_tests' : {},
            'subprojects' : {},
            'project_path' : os.getcwd(),
            'is_external_project' : is_external_project }
  set_extensions( state )
  os.chdir( 'src' )
  evaluate_branch( state )
  if project_type == 'executable':
    driver = None
    for extension in state['implementation_extensions']:
      possible_driver = name + '.' + extension
      if trial in implementation_files:
        driver = possible_driver
        break
    if driver == None:
      raise RuntimeError('Could not determine executable driver')
    state['driver'] = driver
    state['implementation_files'].remove(driver)
  if 'language_revision' in kwargs:
    state['language_revision'] = kwargs['language_revision']
  if 'include_path' in kwargs:
    assert os.path.isdir( kwargs['include_path'] )
    state['include_path'] = kwargs['include_path']
  if not os.path.exists('.metaconfigure'):
    os.makedirs('.metaconfigure')
  serialize( state )
