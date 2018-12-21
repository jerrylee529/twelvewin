#!/bin/bash

export SERVICE_SETTINGS=analysis.config.ProductionConfig

nohup python schedule_manager.py &
