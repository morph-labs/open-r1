# coding=utf-8
# Copyright 2025 The HuggingFace Team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import requests
from typing import List, Optional


class RoutedMorphSandbox:
    """
    Client for the MorphCloud router service that mimics the API of MorphCloud's Sandbox.
    
    This class provides a simple interface to execute code via a central MorphCloud router,
    which manages sandbox creation and cleanup. It allows batch processing of multiple scripts
    in a single request for improved efficiency.
    
    Attributes:
        router_url (str): The URL of the MorphCloud router service.
        timeout (int): Execution timeout in seconds.
        request_timeout (int): HTTP request timeout in seconds.
    """
    
    def __init__(self, router_url: str, timeout: int = 30, request_timeout: int = 60):
        """
        Initialize the routed MorphCloud sandbox client.
        
        Args:
            router_url: The URL of the MorphCloud router, including host and port.
            timeout: Default execution timeout in seconds.
            request_timeout: Default HTTP request timeout in seconds.
        """
        self.router_url = router_url
        self.timeout = timeout
        self.request_timeout = request_timeout
    
    def run_code(self, scripts: List[str], 
                language: str = "python", 
                timeout: Optional[int] = None,
                request_timeout: Optional[int] = None) -> List:
        """
        Execute multiple scripts using MorphCloud via the router.
        
        Args:
            scripts: List of code scripts to execute.
            language: Programming language for the code.
            timeout: Execution timeout in seconds. If None, uses the instance timeout.
            request_timeout: HTTP request timeout in seconds. If None, uses the instance request_timeout.
            
        Returns:
            List of execution results with text and exception_str properties.
        """
        # Use instance variables if parameters are not provided
        actual_timeout = timeout if timeout is not None else self.timeout
        actual_request_timeout = request_timeout if request_timeout is not None else self.request_timeout
        
        # Prepare payload for the router
        payload = {
            "scripts": scripts,
            "language": language,
            "timeout": actual_timeout,
            "request_timeout": actual_request_timeout,
        }
        
        try:
            # Send the request to the MorphCloud Router
            endpoint = f"http://{self.router_url}/execute_batch"
            response = requests.post(endpoint, json=payload, timeout=actual_request_timeout)
            
            if response.status_code != 200:
                # Handle failed request
                error = f"Request to MorphCloud router failed with status code: {response.status_code}"
                print(error)
                
                # Create error results for each script
                results = []
                for _ in scripts:
                    results.append(type('obj', (object,), {
                        'text': None,
                        'exception_str': error
                    }))
                return results
            
            # Parse the response and convert to objects with the expected properties
            response_data = response.json()
            results = []
            
            for item in response_data:
                # Create an object with text and exception_str properties
                result = type('obj', (object,), {
                    'text': item.get('text'),
                    'exception_str': item.get('exception_str')
                })
                results.append(result)
            
            return results
            
        except Exception as e:
            error = f"Error communicating with MorphCloud router: {str(e)}"
            print(error)
            
            # Create error results for each script
            results = []
            for _ in scripts:
                results.append(type('obj', (object,), {
                    'text': None,
                    'exception_str': error
                }))
            return results