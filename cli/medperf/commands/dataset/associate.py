import logging

from medperf.ui.interface import UI
from medperf.comms.interface import Comms
from medperf.entities.dataset import Dataset
from medperf.entities.benchmark import Benchmark
from medperf.utils import dict_pretty_print, pretty_error
from medperf.commands.compatibility_test import CompatibilityTestExecution


class AssociateDataset:
    @staticmethod
    def run(data_uid: str, benchmark_uid: int, comms: Comms, ui: UI):
        """Associates a registered dataset with a benchmark

        Args:
            data_uid (int): UID of the registered dataset to associate
            benchmark_uid (int): UID of the benchmark to associate with
        """
        dset = Dataset(data_uid, ui)
        benchmark = Benchmark.get(benchmark_uid, comms)

        if str(dset.preparation_cube_uid) != str(benchmark.data_preparation):
            pretty_error("The specified dataset wasn't prepared for this benchmark", ui)

        _, _, _, result = CompatibilityTestExecution.run(
            benchmark_uid, comms, ui, data_uid=data_uid
        )
        ui.print("These are the results generated by the compatibility test. ")
        ui.print("This will be sent along the association request.")
        ui.print("They will not be part of the benchmark.")
        dict_pretty_print(result.todict(), ui)

        approval = dset.request_association_approval(benchmark, ui)

        if approval:
            ui.print("Generating dataset benchmark association")
            metadata = {"test_result": result.todict()}
            comms.associate_dset(dset.uid, benchmark_uid, metadata)
        else:
            pretty_error(
                "Dataset association operation cancelled", ui, add_instructions=False
            )
