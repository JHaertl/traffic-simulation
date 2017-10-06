import logging

logger = logging.getLogger('simulation')
logger.setLevel(logging.INFO)
log_file_handler = logging.FileHandler('log.txt', mode='w')
log_file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log_file_handler.setFormatter(formatter)
logger.addHandler(log_file_handler)


def main():
    logger.info('Started simulation.')
    from traffic_simulation import TrafficSimulation
    import config_reader as cr

    cr.initialize()
    simulation = TrafficSimulation()
    simulation.simulate()

    logger.info('Finished simulation.')


if __name__ == "__main__":
    main()
